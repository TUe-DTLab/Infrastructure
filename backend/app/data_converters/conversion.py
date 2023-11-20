import os
import shutil
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app import models
from app.database import StorageManager


def convert_ifc_to_gltf(db: Session, file_id: UUID):
    # setup
    base_dir = Path(__file__).parent.resolve()
    tmp_dir = base_dir / "tmp" / (str(file_id) + "-gltf")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    # retrieve file based on uuid
    source_file_db = db.query(models.FileObject).where(models.FileObject.id == file_id).first()
    source_file_path = StorageManager.get_file(source_file_db.file.path).get_cdn_url()

    # convert to collada
    os.system(
        '"{ifc_convert}" --use-element-guids "{ifc_file}" "{dae_file}" --exclude=entities IfcOpeningElement'.format(
            ifc_convert=base_dir / "IFCConvert" / "IfcConvert",
            ifc_file=source_file_path,
            dae_file=tmp_dir / "output.dae",
        )
    )

    # convert to gltf
    os.system(
        '"{collada2gltf}" --materialsCommon -i "{dae_file}" -o "{gltf_file}"'.format(
            collada2gltf=base_dir / "COLLADA2GLTF" / "COLLADA2GLTF-bin",
            dae_file=tmp_dir / "output.dae",
            gltf_file=tmp_dir / "output.gltf",
        )
    )

    # create new file
    with open(tmp_dir / "output.gltf", "rb") as f:
        file_object = models.FileObject(file=f, model_id=source_file_db.model_id, name=source_file_db.name + "-gltf")
        db.add(file_object)
        db.commit()
    db.refresh(file_object)

    # cleanup
    shutil.rmtree(tmp_dir)

    # return file object
    return file_object


def convert_ifc_to_ttl(db: Session, file_id: UUID):
    # setup
    base_dir = Path(__file__).parent.resolve()
    tmp_dir = base_dir / "tmp" / (str(file_id) + "-ttl")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    # retrieve file based on uuid
    source_file_db = db.query(models.FileObject).where(models.FileObject.id == file_id).first()
    source_file_path = StorageManager.get_file(source_file_db.file.path).get_cdn_url()

    # copy file to tmp dir (cause the tool will append .ifc otherwise, and will not be able to find the file)
    shutil.copyfile(source_file_path, tmp_dir / "input.ifc")

    # convert file to ttl
    os.system(
        'java -jar "{ifc_to_lbd}" "{ifc_file}" "{ttl_file}"'.format(
            ifc_to_lbd=base_dir / "IFCtoLBD" / "IFCtoLBD-0.1-shaded.jar",
            ifc_file=tmp_dir / "input.ifc",
            ttl_file=tmp_dir / "output.ttl",
        )
    )

    # create new file
    with open(tmp_dir / "output.ttl", "rb") as f:
        file_object = models.FileObject(file=f, model_id=source_file_db.model_id, name=source_file_db.name + "-ttl")
        db.add(file_object)
        db.commit()
    db.refresh(file_object)

    # cleanup
    # shutil.rmtree(tmp_dir)

    # return file object
    return file_object
