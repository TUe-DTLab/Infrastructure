#!/usr/bin/bash

ROOT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo $ROOT_DIR

# Setup IFCConvert
rm -rf "$ROOT_DIR/IFCConvert"
wget "https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-9cc1f5f-linux64.zip" -P "$ROOT_DIR"
mkdir "$ROOT_DIR/IFCConvert"
unzip "$ROOT_DIR/IfcConvert-v0.7.0-9cc1f5f-linux64.zip" -d "$ROOT_DIR/IFCConvert"
rm "$ROOT_DIR/IfcConvert-v0.7.0-9cc1f5f-linux64.zip"

# Setup COLLADA2GLTF
rm -rf "$ROOT_DIR/COLLADA2GLTF"
wget "https://github.com/KhronosGroup/COLLADA2GLTF/releases/download/v2.1.5/COLLADA2GLTF-v2.1.5-linux.zip" -P "$ROOT_DIR"
mkdir "$ROOT_DIR/COLLADA2GLTF"
unzip "$ROOT_DIR/COLLADA2GLTF-v2.1.5-linux.zip" -d "$ROOT_DIR/COLLADA2GLTF"
rm "$ROOT_DIR/COLLADA2GLTF-v2.1.5-linux.zip"

# Setup IFC components
# TODO

# Setup IFCtoLBD
rm -rf "$ROOT_DIR/IFCtoLDB"
mkdir "$ROOT_DIR/IFCtoLBD"
wget "https://github.com/pipauwel/IFCtoLBD/releases/download/IFCtoLBD-0.1/IFCtoLBD-0.1-shaded.jar" -P "$ROOT_DIR/IFCtoLBD"