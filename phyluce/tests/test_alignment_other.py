#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(c) 2021 Brant Faircloth || http://faircloth-lab.org/
All rights reserved.

This code is distributed under a 3-clause BSD license. Please see
LICENSE.txt for more information.

Created on 2021-02-14 T10:44:15-06:00
"""


import os
import re
import glob
import shutil
import platform
import subprocess
import logging

import pytest
from Bio import AlignIO

import pdb


@pytest.fixture(autouse=True)
def cleanup_files(request):
    """cleanup extraneous log files"""

    def clean():
        log_files = os.path.join(
            request.config.rootdir, "phyluce", "tests", "*.log"
        )
        for file in glob.glob(log_files):
            os.remove(file)

    request.addfinalizer(clean)


@pytest.fixture(scope="module")
def o_dir(request):
    directory = os.path.join(
        request.config.rootdir, "phyluce", "tests", "test-observed"
    )
    os.mkdir(directory)

    def clean():
        shutil.rmtree(directory)

    request.addfinalizer(clean)
    return directory


@pytest.fixture(scope="module")
def e_dir(request):
    directory = os.path.join(
        request.config.rootdir, "phyluce", "tests", "test-expected"
    )
    return directory


@pytest.mark.skipif(
    platform.processor() == "arm64", reason="Won't run on arm64"
)
def test_align_gblocks_trim(o_dir, e_dir, request):
    program = (
        "bin/align/phyluce_align_get_gblocks_trimmed_alignments_from_untrimmed"
    )
    output = os.path.join(o_dir, "mafft-gblocks")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    for output_file in glob.glob(os.path.join(output, "*")):
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-gblocks", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_trimal_trim(o_dir, e_dir, request):
    program = (
        "bin/align/phyluce_align_get_trimal_trimmed_alignments_from_untrimmed"
    )
    output = os.path.join(o_dir, "mafft-trimal")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    for output_file in glob.glob(os.path.join(output, "*")):
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-trimal", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_edge_trim(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_get_trimmed_alignments_from_untrimmed"
    output = os.path.join(o_dir, "mafft-edge-trim")
    # note that thus only uses alignemnts with an odd
    # number of taxa so ties in base composition at a
    # column do not cause random differences in expected output
    # this also completes testing of generic_align and seqalign
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-for-edge-trim"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    for output_file in glob.glob(os.path.join(output, "*")):
        name = os.path.basename(output_file)
        print(name)
        expected_file = os.path.join(e_dir, "mafft-edge-trim", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_missing_data_designators(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_add_missing_data_designators"
    output = os.path.join(o_dir, "mafft-missing-data-designators")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--match-count-output",
        os.path.join(e_dir, "taxon-set.incomplete.conf"),
        "--incomplete-matrix",
        os.path.join(e_dir, "taxon-set.incomplete"),
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    for output_file in glob.glob(os.path.join(output, "*")):
        name = os.path.basename(output_file)
        print(name)
        expected_file = os.path.join(
            e_dir, "mafft-missing-data-designators", name
        )
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_convert_degen_bases(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_convert_degen_bases"
    output = os.path.join(o_dir, "mafft-degen-bases-converted")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-degen-bases"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    for output_file in glob.glob(os.path.join(output, "*")):
        name = os.path.basename(output_file)
        print(name)
        expected_file = os.path.join(
            e_dir, "mafft-degen-bases-converted", name
        )
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_convert_align_mafft_fasta_to_nexus(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_convert_one_align_to_another"
    output = os.path.join(o_dir, "mafft-fasta-to-nexus")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    for output_file in glob.glob(os.path.join(output, "*")):
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-fasta-to-nexus", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_convert_align_mafft_fasta_to_phylip_relaxed(
    o_dir, e_dir, request
):
    program = "bin/align/phyluce_align_convert_one_align_to_another"
    output = os.path.join(o_dir, "mafft-fasta-to-phylip-relaxed")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "phylip-relaxed",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    for output_file in glob.glob(os.path.join(output, "*")):
        name = os.path.basename(output_file)
        expected_file = os.path.join(
            e_dir, "mafft-fasta-to-phylip-relaxed", name
        )
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_convert_align_mafft_nexus_to_fasta(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_convert_one_align_to_another"
    output = os.path.join(o_dir, "mafft-nexus-to-fasta")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-fasta-to-nexus"),
        "--output",
        output,
        "--input-format",
        "nexus",
        "--output-format",
        "fasta",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    for output_file in glob.glob(os.path.join(output, "*")):
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-nexus-to-fasta", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected
