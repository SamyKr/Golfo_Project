from osgeo import gdal
import os
import gps_image as gi

gdal.UseExceptions()

def crop_vrt(image_path, vrt_path, output_jp2, output_png, width=2500, height=2500, offset_x=200):
    if not os.path.exists(image_path):
        print(f"❌ L'image spécifiée n'existe pas : {image_path}")
        return
    
    if not os.path.exists(vrt_path):
        print(f"❌ Le fichier VRT spécifié n'existe pas : {vrt_path}")
        return
    
    try:
        gps_data = gi.extract_gps_from_image(image_path)
        if not gps_data:
            print("❌ Aucune donnée GPS trouvée dans l'image.")
            return

        center_lon = gps_data['X_Lambert'] - offset_x
        center_lat = gps_data['Y_Lambert']

        print(f"📍 Coordonnées GPS extraites (après offset) : Latitude {center_lat}, Longitude {center_lon}")

        xmin = center_lon - width
        xmax = center_lon
        ymin = center_lat - (height / 2)
        ymax = center_lat + (height / 2)

        warp_options_jp2 = gdal.WarpOptions(
            format="JP2OpenJPEG",
            outputBounds=[xmin, ymin, xmax, ymax],
            outputType=gdal.GDT_Byte,
            xRes=1,
            yRes=1,
            warpMemoryLimit=500,
            creationOptions=[
                "QUALITY=50",
                "REVERSIBLE=YES",
                "BlockXSIZE=512",
                "BlockYSIZE=512"
            ]
        )

        warp_options_png = gdal.WarpOptions(
            format="PNG",
            outputBounds=[xmin, ymin, xmax, ymax],
            outputType=gdal.GDT_Byte,
            xRes=1,
            yRes=1
        )

        output_dir = os.path.dirname(output_jp2)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        gdal.Warp(destNameOrDestDS=output_jp2, srcDSOrSrcDSTab=vrt_path, options=warp_options_jp2)
        print(f"✅ Fichier JP2 compressé créé avec succès : {output_jp2}")

        gdal.Warp(destNameOrDestDS=output_png, srcDSOrSrcDSTab=vrt_path, options=warp_options_png)
        print(f"✅ Fichier PNG créé avec succès : {output_png}")

    except Exception as e:
        print(f"❌ Erreur lors du traitement : {str(e)}")
    return output_png

# exemple
if __name__ == "__main__":
    image_file = "test.jpg"
    vrt_file = "output/fichier_vrt3.vrt"
    output_jp2 = "output/sortie344.jp2"
    output_png = "output/sortie344pn.png"

    crop_vrt(image_file, vrt_file, output_jp2, output_png)
