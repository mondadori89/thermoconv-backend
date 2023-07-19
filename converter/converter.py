import numpy as np
from converter.thermal import Thermal
from PIL import Image, ExifTags
import os
import subprocess


# Biblioteca do amigão: https://github.com/SanNianYiSi/thermal_parser  encontrado no vídeo: https://www.youtube.com/watch?v=ulnPtSWGg18

def convert_jpg_tiff(inputs_folder, outputs_folder):

    thermal = Thermal(
    dirp_filename='converter/plugins/dji_thermal_sdk_v1.1_20211029/linux/release_x64/libdirp.so',
    dirp_sub_filename='converter/plugins/dji_thermal_sdk_v1.1_20211029/linux/release_x64/libv_dirp.so',
    iirp_filename='converter/plugins/dji_thermal_sdk_v1.1_20211029/linux/release_x64/libv_iirp.so',
    exif_filename=None,
    dtype=np.float32,
)

    for imagename in os.listdir(inputs_folder):
        if imagename.endswith('.JPG'):
            image_without_extension = os.path.splitext(imagename)[0]
            print(image_without_extension)

            # creating each TIFF file
            temperature = thermal.parse_dirp2(image_filename=f'{inputs_folder}/{image_without_extension}.JPG', m2ea_mode='true')
            """
            Parameters can be added to the line above, as relative_humidity, emissivity, etc
            image_filename: str,
            image_height: int = 512,
            image_width: int = 640,
            object_distance: float = 5.0,
            relative_humidity: float = 70.0,
            emissivity: float = 1.0,
            reflected_apparent_temperature: float = 23.0,
            m2ea_mode: bool = False,
            """
            assert isinstance(temperature, np.ndarray)

            image_matrix = temperature.reshape(512, 640)

            im = Image.fromarray(image_matrix)
            im.save(f"{outputs_folder}/{image_without_extension}.tiff")


            # coping the exif data from the JPG to the TIFF file
            jpg_file = os.path.join(inputs_folder, image_without_extension) + '.JPG'
            print(jpg_file)
            tiff_file = os.path.join(outputs_folder, image_without_extension) + '.tiff'
            print(tiff_file)

            exiftool_cmd = ['exiftool', '-tagsfromfile', jpg_file, '-gps*', '-ext', 'tiff', tiff_file]
                    
            result = subprocess.run(exiftool_cmd, capture_output=True, text=True)

            output = result.stdout
            error = result.stderr

            print("Output:", output)
            print("Error:", error) 



