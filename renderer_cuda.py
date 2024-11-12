'''
Part of the code (CUDA and OpenGL memory transfer) is derived from https://github.com/jbaron34/torchwindow/tree/master
'''
from OpenGL import GL as gl
import OpenGL.GL.shaders as shaders
import util
import util_gau
import numpy as np
import torch
from renderer_ogl import GaussianRenderBase
from dataclasses import dataclass
from cuda import cudart as cu
from diff_gaussian_rasterization import GaussianRasterizationSettings, GaussianRasterizer


VERTEX_SHADER_SOURCE = """
#version 450

smooth out vec4 fragColor;
smooth out vec2 texcoords;

vec4 positions[3] = vec4[3](
    vec4(-1.0, 1.0, 0.0, 1.0),
    vec4(3.0, 1.0, 0.0, 1.0),
    vec4(-1.0, -3.0, 0.0, 1.0)
);

vec2 texpos[3] = vec2[3](
    vec2(0, 0),
    vec2(2, 0),
    vec2(0, 2)
);

void main() {
    gl_Position = positions[gl_VertexID];
    texcoords = texpos[gl_VertexID];
}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330

smooth in vec2 texcoords;

out vec4 outputColour;

uniform sampler2D texSampler;

void main()
{
    outputColour = texture(texSampler, texcoords);
}
"""

def quaternion_multiply(a, b):
    a_norm=torch.nn.functional.normalize(a)
    b_norm=torch.nn.functional.normalize(b)
    w1, x1, y1, z1 = a_norm[:, 0], a_norm[:, 1], a_norm[:, 2], a_norm[:, 3]
    w2, x2, y2, z2 = b_norm[:, 0], b_norm[:, 1], b_norm[:, 2], b_norm[:, 3]

    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2

    return torch.stack([w, x, y, z], dim=1)

@dataclass
class GaussianDataCUDA:
    xyz: torch.Tensor
    rot: torch.Tensor
    scale: torch.Tensor
    opacity: torch.Tensor
    sh: torch.Tensor
    
    def __len__(self):
        return len(self.xyz)
    
    @property 
    def sh_dim(self):
        return self.sh.shape[-2]
    
    @torch.no_grad()
    def get_xyz_bound(self, percentile=86.6):
        half_percentile = (100 - percentile) / 200
        return torch.quantile(self.xyz,half_percentile,dim=0), torch.quantile(self.xyz,1 - half_percentile,dim=0)

    def clone(self):
        return GaussianDataCUDA(
            xyz=self.xyz.clone(),
            rot=self.rot.clone(),
            scale=self.scale.clone(),
            opacity=self.opacity.clone(),
            sh=self.sh.clone(),
        )
    
@dataclass
class GaussianRasterizationSettingsStorage:
    image_height: int
    image_width: int 
    tanfovx : float
    tanfovy : float
    bg : torch.Tensor
    scale_modifier : float
    viewmatrix : torch.Tensor
    projmatrix : torch.Tensor
    sh_degree : int
    campos : torch.Tensor
    prefiltered : bool
    debug : bool


def gaus_cuda_from_cpu(gau: util_gau) -> GaussianDataCUDA:
    gaus =  GaussianDataCUDA(
        xyz = torch.tensor(gau.xyz).float().cuda().requires_grad_(False),
        rot = torch.tensor(gau.rot).float().cuda().requires_grad_(False),
        scale = torch.tensor(gau.scale).float().cuda().requires_grad_(False),
        opacity = torch.tensor(gau.opacity).float().cuda().requires_grad_(False),
        sh = torch.tensor(gau.sh).float().cuda().requires_grad_(False)
    )
    gaus.sh = gaus.sh.reshape(len(gaus), -1, 3).contiguous()
    return gaus
    

class CUDARenderer(GaussianRenderBase):
    def __init__(self, w, h):
        super().__init__()
        self.raster_settings = {
            "image_height": int(h),
            "image_width": int(w),
            "tanfovx": 1,
            "tanfovy": 1,
            "bg": torch.Tensor([0., 0., 0]).float().cuda(),
            "scale_modifier": 1.,
            "viewmatrix": None,
            "projmatrix": None,
            "sh_degree": 1,  # ?
            "campos": None,
            "prefiltered": False,
            "debug": False
        }
        # gl.glViewport(0, 0, w, h)
        # self.program = util.compile_shaders(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)
        # setup cuda
        # err, *_ = cu.cudaGLGetDevices(1, cu.cudaGLDeviceList.cudaGLDeviceListAll)
        # if err == cu.cudaError_t.cudaErrorUnknown:
        #     raise RuntimeError(
        #         "OpenGL context may be running on integrated graphics"
        #     )
        
        # self.vao = gl.glGenVertexArrays(1)
        self.tex = None
        self.NTC = None
        # the index of NTCs and additional_3dgs is the index of the current un-processed frame.
        self.NTCs = []
        self.additional_3dgs = []
        self.current_timestep=0
        # self.set_gl_texture(h, w)

        # gl.glDisable(gl.GL_CULL_FACE)
        # gl.glEnable(gl.GL_BLEND)
        # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def update_gaussian_data(self, gaus: util_gau.GaussianData):
        self.gaussians = gaus_cuda_from_cpu(gaus)
        self.init_gaussians = GaussianDataCUDA(
                                xyz = self.gaussians.xyz.clone(),
                                rot = self.gaussians.rot.clone(),
                                scale = self.gaussians.scale.clone(),
                                opacity = self.gaussians.opacity.clone(),
                                sh = self.gaussians.sh.clone()
                            )
        self.raster_settings["sh_degree"] = int(np.round(np.sqrt(self.gaussians.sh_dim))) - 1

    def sort_and_update(self, camera: util.Camera):
        pass
    
    def set_scale_modifier(self, modifier):
        self.raster_settings["scale_modifier"] = float(modifier)

    def set_render_mod(self, mod: int):
        pass
    
    def set_gl_texture(self, h, w):
        self.tex = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGBA32F,
            w,
            h,
            0,
            gl.GL_RGBA,
            gl.GL_FLOAT,
            None,
        )
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        err, self.cuda_image = cu.cudaGraphicsGLRegisterImage(
            self.tex,
            gl.GL_TEXTURE_2D,
            cu.cudaGraphicsRegisterFlags.cudaGraphicsRegisterFlagsWriteDiscard,
        )
        if err != cu.cudaError_t.cudaSuccess:
            raise RuntimeError("Unable to register opengl texture")
    
    def set_render_reso(self, w, h):
        self.raster_settings["image_height"] = int(h)
        self.raster_settings["image_width"] = int(w)
        gl.glViewport(0, 0, w, h)
        self.set_gl_texture(h, w)
    
    @torch.no_grad()    
    def query_NTC(self, xyz, timestep):
        mask, d_xyz, d_rot = self.NTCs[timestep](xyz)
        self.gaussians.xyz += d_xyz
        self.gaussians.rot = quaternion_multiply(self.gaussians.rot, d_rot)

    @torch.no_grad()    
    def cat_additions(self, timestep):
        additions=self.additional_3dgs[timestep]
        s2_gaussians=GaussianDataCUDA(
            xyz=torch.cat([additions.xyz, self.gaussians.xyz], dim=0),
            rot=torch.cat([additions.rot, self.gaussians.rot], dim=0),
            scale=torch.cat([additions.scale, self.gaussians.scale], dim=0),
            opacity=torch.cat([additions.opacity, self.gaussians.opacity], dim=0),
            sh=torch.cat([additions.sh, self.gaussians.sh], dim=0)
        )
        return s2_gaussians
    
    def fvv_reset(self):
        self.gaussians = self.init_gaussians.clone()
        self.current_timestep=0
        
    def update_camera_pose(self, camera: util.Camera):
        view_matrix = camera.get_view_matrix()
        view_matrix[[0, 2], :] = -view_matrix[[0, 2], :]
        proj = camera.get_project_matrix() @ view_matrix
        self.raster_settings["viewmatrix"] = torch.tensor(view_matrix.T).float().cuda()
        self.raster_settings["campos"] = torch.tensor(camera.position).float().cuda()
        self.raster_settings["projmatrix"] = torch.tensor(proj.T).float().cuda()

    def update_camera_intrin(self, camera: util.Camera):
        view_matrix = camera.get_view_matrix()
        view_matrix[[0, 2], :] = -view_matrix[[0, 2], :]
        proj = camera.get_project_matrix() @ view_matrix
        self.raster_settings["projmatrix"] = torch.tensor(proj.T).float().cuda()
        hfovx, hfovy, focal = camera.get_htanfovxy_focal()
        self.raster_settings["tanfovx"] = hfovx
        self.raster_settings["tanfovy"] = hfovy

    def draw(self, timestep: int = 0):
        raster_settings = GaussianRasterizationSettings(**self.raster_settings)
        rasterizer = GaussianRasterizer(raster_settings=raster_settings)
        # means2D = torch.zeros_like(self.gaussians.xyz, dtype=self.gaussians.xyz.dtype, requires_grad=False, device="cuda")
        rendered_gaussians = self.gaussians
        with torch.no_grad():
            while(timestep-self.current_timestep>0):
                self.query_NTC(self.gaussians.xyz, self.current_timestep)
                self.current_timestep+=1
            if self.current_timestep!=0:
                rendered_gaussians=self.cat_additions(self.current_timestep-1)
            img, radii = rasterizer(
                means3D = rendered_gaussians.xyz,
                means2D = None,
                shs = rendered_gaussians.sh,
                colors_precomp = None,
                opacities = rendered_gaussians.opacity,
                scales = rendered_gaussians.scale,
                rotations = rendered_gaussians.rot,
                cov3D_precomp = None
            )
        img = img.permute(1, 2, 0)
        img = torch.concat([img, torch.ones_like(img[..., :1])], dim=-1)
        img = img.contiguous()
        height, width = img.shape[:2]
        # transfer
        (err,) = cu.cudaGraphicsMapResources(1, self.cuda_image, cu.cudaStreamLegacy)
        if err != cu.cudaError_t.cudaSuccess:
            raise RuntimeError("Unable to map graphics resource")
        err, array = cu.cudaGraphicsSubResourceGetMappedArray(self.cuda_image, 0, 0)
        if err != cu.cudaError_t.cudaSuccess:
            raise RuntimeError("Unable to get mapped array")
        
        (err,) = cu.cudaMemcpy2DToArrayAsync(
            array,
            0,
            0,
            img.data_ptr(),
            4 * 4 * width,
            4 * 4 * width,
            height,
            cu.cudaMemcpyKind.cudaMemcpyDeviceToDevice,
            cu.cudaStreamLegacy,
        )
        if err != cu.cudaError_t.cudaSuccess:
            raise RuntimeError("Unable to copy from tensor to texture")
        (err,) = cu.cudaGraphicsUnmapResources(1, self.cuda_image, cu.cudaStreamLegacy)
        if err != cu.cudaError_t.cudaSuccess:
            raise RuntimeError("Unable to unmap graphics resource")

        gl.glUseProgram(self.program)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex)
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
