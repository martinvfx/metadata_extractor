#!/usr/bin/env python 3.10
##########################################################################
## Script to get metadata from EXR sequences or others kind of files    ##
## requerimets: OpenImageIO (aka oiio ) custom build                    ##
## Autor: Martin Elias Iglesias  martin@vfx-sup.com                     ##
## version 001 2023-04-10                                               ##
##########################################################################
import collections
import os
import argparse
import oiio
import logging
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
logging.basicConfig(level=logging.INFO)

usable_extensions = ['exr', 'arw', 'raw', 'dng']

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=False, default=os.getcwd(),
    help="path to desired directory of images sequences with metadata")
ap.add_argument("-l", "--lens_list", required=False,
    help='path to the .txt file with all lens serial numbers and his mm equivalent, i.e: \"Z50108175 = 29mm\" ') #TO-DO: implementar un chequeo de si exite la lista y sacar los valores de cada lente.
ap.add_argument("-t", "--type", required=False, default='exr',
    help="desired file extension for get metadata; default it is EXR")

args = vars(ap.parse_args())
working_folder = args["images"]
extension = args["type"]
extension = extension.replace('.', '').lower()

if working_folder.endswith('\\'):
    pass
else:
    working_folder = working_folder + '\\'
    logging.debug(f"\nworking folder is: {working_folder}")


def createXML(path):

    xml_filename = []
    root_xml = ET.Element("Sequence MetaData")

    # Loop through each file in the image sequence
    for filename in os.listdir(path):
        if os.path.isfile(filename):
            if filename.endswith("."+extension): #TO-DO: Make aviable for filename.endswith(".dng") or filename.endswith(".ARW"):
                logging.debug(f'\tfilename = {filename.lower()}')
                logging.debug(f'\nExtractig metadata from {filename} and placing into XML file.')

                try:
                    # Open the image file
                    image = oiio.ImageInput.open(os.path.join(path, filename))
                    spec = image.spec()

                    if not image:
                        print("Could not open", filename)
                        continue
                except:
                    logging.warning(f'\ncould not open or read metadata in this file: {filename}')
                    quit()

                # Get the metadata for the image
                metadata = {}
                for meta in spec.extra_attribs:
                    metadata[meta.name] = meta.value
                    # logging.info(f'\t metadata Key:  {meta.name} == {meta.value}') # .attribute(meta.name, meta.type, meta.value)

                # Reorder metadata for better and fast read.
                order_metadata = ['focalLength', 'lens', 'roll', 'tilt', 'focal', 'lens_type']
                # logging.debug(f'find parts \t {[z for z in [x.find("lens") for x in order_metadata] if z is not -1]}  --- {order_metadata[1]}')
                logging.debug(f' check items { [i for i in metadata.keys() if i in order_metadata] }')


                for k,v in metadata.items():
                    for p in order_metadata:
                        if p.lower() in k.lower():
                            logging.debug(f'k = {k} {v} \t p={p} \t== {metadata[k]} ')
                            # construct a new temp dictionary from relevant keys.
                            metadata_temp = {p:v} # type(metadata) ((i, metadata.get(k)) for i in order_metadata)
                            # Merge all metadata y one dictionary.
                            metadata = metadata_temp | metadata
                        else:
                            pass
                logging.debug("\n________")

                # ET.tostring(root_xml, encoding='utf8').decode('utf8')
                filename_field = ET.SubElement(root_xml, f"metadata from file: {filename}")

                # Create an XML element for the metadata
                for key, value in metadata.items():
                    child = ET.SubElement(filename_field, key)
                    child.text = str(value)

                # Close the image file
                image.close()

                xml_filename.append(filename.split('.')[0].rstrip('1234567890') )

                # else:
                #     logging.error(f"\nNo images in this folder:\n{path}\n") #TO-DO: fix because its showing when the folder has other kind of files.

                ET.indent(root_xml, space="\t", level=0)
                ET.indent(filename_field, space="\t", level=1)
            elif '.' in filename and filename.split(".", 1)[1].lower() not in usable_extensions  :
                logging.warning(f'\t {filename} is not an image extension usable in this tool')
            # else:
            #     pass

    # Write the metadata to an XML file
    logging.info(f'\txml_filename == {xml_filename}')
    if  xml_filename:
        xml_filename = xml_filename[0] + 'metadata' + ".xml"
        xml_path = os.path.join(path, xml_filename)
        tree = ET.ElementTree(root_xml) # xml_data
        # ET.tostring(root_xml, encoding='utf8').decode('utf8')
        ET.tostring(root_xml, encoding='unicode')
        tree.write(xml_path)
        logging.info(f'\nExtractig metadata from {filename} and placing into XML file {xml_filename}.')


if __name__ == '__main__':
    createXML(working_folder) # path

    # Set the path to image sequence
    path = "E:/temp/seq_con_metadata_test"  # This variable is only for test purpose.
    # createXML(path) # only for test and debug purpose.



















