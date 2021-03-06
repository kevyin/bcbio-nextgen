"""Handle extraction of final files from processing pipelines into storage.
"""
import datetime
import os

from bcbio.upload import shared, filesystem, galaxy

_approaches = {"filesystem": filesystem,
               "galaxy": galaxy}

def from_sample(sample):
    """Upload results of processing from an analysis pipeline sample.
    """
    upload_config = sample["info"].get("upload")
    if upload_config:
        approach = _approaches[upload_config.get("method", "filesystem")]
        for finfo in _get_files(sample):
            approach.update_file(finfo, sample["info"], upload_config)

# ## File information from sample

def _get_files(sample):
    """Retrieve files for the sample, dispatching by analysis type.

    Each file is a dictionary containing the path plus associated
    metadata about the file and pipeline versions.
    """
    analysis = sample["info"].get("analysis")
    if analysis in ["variant", "SNP calling"]:
        return _get_files_variantcall(sample)
    else:
        return []

def _add_meta(xs, sample):
    out = []
    for x in xs:
        x["mtime"] = shared.get_file_timestamp(x["path"])
        x["sample"] = sample["name"][-1]
        out.append(x)
    return out

def _get_files_variantcall(sample):
    """Return output files for the variant calling pipeline.
    """
    out = [{"path": sample["summary"]["pdf"],
            "type": "pdf",
            "ext": "summary"},
            {"path": sample["work_bam"],
             "type": "bam",
             "ext": "ready"}]
    for x in sample["variants"]:
        out.append({"path": x["vrn_file"],
                    "type": "vcf",
                    "ext": x["variantcaller"],
                    "variantcaller": x["variantcaller"]})
    return _add_meta(out, sample)
