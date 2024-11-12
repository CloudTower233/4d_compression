from encode import encode_images_to_h265
from split import split
from copying import copy_images,copy_csv
from decode import decode
from decompress import decompress
from merge import merge

def postprocess():
    copy_images()
    copy_csv()
    split()
    encode_images_to_h265()
    decode()
    merge()
    decompress()

if __name__ == "__main__":
    postprocess()