#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is part of Robobackup.
Copyright 2015 Siegfried Schoefer

Robobackup is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robobackup is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import unittest.mock as mock
import os
import sys
import gettext
import xml

import parser_robobackup_xml
import robobackup

from subprocess import CalledProcessError, DEVNULL, call

class HelperFunctionsInParser(unittest.TestCase):

    def setUp(self):
        os.chdir(sys.path[0])
        translation = gettext.translation("robobackup", "locale", ["de"])
        translation.install()
        os.chdir("resources")
        os.chdir("tests")
    
    def test_strip(self):
       self.assertEqual(parser_robobackup_xml.strip("   \t test  \n\t"), "test")

    @mock.patch("parser_robobackup_xml.check_output", autospec=True)
    def test_get_dict_drivename_to_letter_one_name(self, mock_check_output):
        with open("test_get_dict_drivename_to_letter_1.txt", "r", encoding="UTF-16") as file:
            data = file.read()
            mock_check_output.return_value = data
        dict_drivename_letter = parser_robobackup_xml.get_dict_drivename_to_letter()
        mock_check_output.assert_called_with(\
            "wmic logicaldisk get caption, volumename", \
            shell=True, universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
        self.assertEqual(dict_drivename_letter, {'backup': ['E']})

    @mock.patch("parser_robobackup_xml.check_output", autospec=True)
    def test_get_dict_drivename_to_letter_two_names(self, mock_check_output):
        with open("test_get_dict_drivename_to_letter_2.txt", "r", encoding="UTF-16") as file:
            data = file.read()
            mock_check_output.return_value = data
        dict_drivename_letter = parser_robobackup_xml.get_dict_drivename_to_letter()
        mock_check_output.assert_called_with(\
            "wmic logicaldisk get caption, volumename", \
            shell=True, universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
        self.assertEqual(dict_drivename_letter, {'backup': ['E', 'F']})

    @mock.patch("parser_robobackup_xml.check_output", autospec=True)
    def test_get_dict_drivename_to_letter_no_names(self, mock_check_output):
        with open("test_get_dict_drivename_to_letter_3.txt", "r", encoding="UTF-16") as file:
            data = file.read()
            mock_check_output.return_value = data
        dict_drivename_letter = parser_robobackup_xml.get_dict_drivename_to_letter()
        mock_check_output.assert_called_with(\
            "wmic logicaldisk get caption, volumename", \
            shell=True, universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
        self.assertEqual(dict_drivename_letter, {})

    @mock.patch("parser_robobackup_xml.check_output", autospec=True)
    def test_get_dict_drivename_to_letter_garbage_wmic(self, mock_check_output):
        mock_check_output.return_value = "@garbage@"
        dict_drivename_letter = parser_robobackup_xml.get_dict_drivename_to_letter()
        mock_check_output.assert_called_with(\
            "wmic logicaldisk get caption, volumename", \
            shell=True, universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
        self.assertEqual(dict_drivename_letter, {})

    @mock.patch("parser_robobackup_xml.get_dict_drivename_to_letter", autospec=True)
    def test_get_driveletter_one(self, mock_get_dict_drivename_to_letter):
        mock_get_dict_drivename_to_letter.return_value = {'backup': ['E']}
        driveletter = parser_robobackup_xml.get_driveletter("BaCKuP")
        self.assertEqual(driveletter, "E")

    @mock.patch("parser_robobackup_xml.get_dict_drivename_to_letter", autospec=True)
    def test_get_driveletter_no_one(self, mock_get_dict_drivename_to_letter):
        mock_get_dict_drivename_to_letter.return_value = {}
        driveletter = parser_robobackup_xml.get_driveletter("BaCkuP")
        self.assertEqual(driveletter, None)

    @mock.patch("parser_robobackup_xml.get_dict_drivename_to_letter", autospec=True)
    def test_get_driveletter_two(self, mock_get_dict_drivename_to_letter):
        mock_get_dict_drivename_to_letter.return_value = {'backup': ['E', 'F']}
        self.assertRaises(RuntimeError, parser_robobackup_xml.get_driveletter, "BACKuP")

    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_parse_location_xor_equal_defined(self, mock_find):
        def side_effect(mediumtype, keyname):
            test = xml.etree.ElementTree.Element("test")
            if keyname == "keyname//external":
                return test
            if keyname == "keyname//internal":
                return test
            return None
        mock_find.side_effect = side_effect
        mediumtype = xml.etree.ElementTree.Element("test")
        self.assertRaises(RuntimeError, parser_robobackup_xml.parse_location, mediumtype, "keyname")

    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_parse_location_xor_equal_not_defined(self, mock_find):
        def side_effect(mediumtype, keyname):
            test = xml.etree.ElementTree.Element("test")
            if keyname == "keyname//external":
                return None
            if keyname == "keyname//internal":
                return None
            return test
        mock_find.side_effect = side_effect
        mediumtype = xml.etree.ElementTree.Element("test")
        self.assertRaises(RuntimeError, parser_robobackup_xml.parse_location, mediumtype, "keyname")

    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_parse_location_internal_empty(self, mock_find):
        def side_effect(mediumtype, keyname):
            test = xml.etree.ElementTree.Element("test")
            test.text=""
            if keyname == "keyname//external":
                return None
            if keyname == "keyname//internal":
                return test
            return None
        mock_find.side_effect = side_effect
        mediumtype = xml.etree.ElementTree.Element("test")
        self.assertRaises(RuntimeError, parser_robobackup_xml.parse_location, mediumtype, "keyname")

    @mock.patch("os.path.isabs", autospec=True)
    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_parse_location_internal_abs(self, mock_find, mock_os):
        def side_effect(mediumtype, keyname):
            test = xml.etree.ElementTree.Element("test")
            test.text="abs"
            if keyname == "keyname//external":
                return None
            if keyname == "keyname//internal":
                return test
            return None
        mock_find.side_effect = side_effect
        mock_os.return_value = True
        mediumtype = xml.etree.ElementTree.Element("test")
        self.assertEqual(parser_robobackup_xml.parse_location(mediumtype, "keyname"), "abs")

    @mock.patch("os.path.isabs", autospec=True)
    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_parse_location_internal_rel(self, mock_find, mock_os):
        def side_effect(mediumtype, keyname):
            test = xml.etree.ElementTree.Element("test")
            test.text="rel"
            if keyname == "keyname//external":
                return None
            if keyname == "keyname//internal":
                return test
            return None
        mock_find.side_effect = side_effect
        mock_os.return_value = False
        mediumtype = xml.etree.ElementTree.Element("test")
        self.assertEqual(parser_robobackup_xml.parse_location(mediumtype, "keyname"), \
            os.path.join(sys.path[0], "rel"))

    @mock.patch("parser_robobackup_xml.get_driveletter", autospec=True)
    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_parse_location_external_empty(self, mock_find, mock_get_path):
        def side_effect(mediumtype, keyname):
            test = xml.etree.ElementTree.Element("test")
            s1 = xml.etree.ElementTree.SubElement(test, "drivename")
            s1.text = "a"
            s2 = xml.etree.ElementTree.SubElement(test, "pathondrive")
            s2.text = "b"
            if keyname == "keyname//external":
                return test
            if keyname == "keyname//internal":
                return None
            return None
        mock_find.side_effect = side_effect
        mock_get_path.return_value = None
        mediumtype = xml.etree.ElementTree.Element("test")
        self.assertEqual(parser_robobackup_xml.parse_location(mediumtype, "keyname"), None)

    @mock.patch("parser_robobackup_xml.get_driveletter", autospec=True)
    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_parse_location_external(self, mock_find, mock_get_path):
        def side_effect(mediumtype, keyname):
            test = xml.etree.ElementTree.Element("test")
            if keyname == "keyname//external":
                return test
            if keyname == "keyname//internal":
                return None
            if keyname == "drivename":
                test.text = "dname"
                return test
            if keyname == "pathondrive":
                test.text = "path"
                return test
            return None
        mock_find.side_effect = side_effect
        mock_get_path.return_value = "c"
        mediumtype = xml.etree.ElementTree.Element("test")
        self.assertEqual(parser_robobackup_xml.parse_location(mediumtype, "keyname"), "c:\\path")
        mock_get_path.assert_called_with("dname")

    @mock.patch.object(xml.etree.ElementTree.Element, "findall", autospec=True)
    def test_get_list(self, mock_find):
        test1 = xml.etree.ElementTree.Element("test1")
        test1.text = "a"
        test2 = xml.etree.ElementTree.Element("test2")
        test2.text = "b"
        mock_find.return_value = [test1, test2]
        self.assertEqual(parser_robobackup_xml.get_list(test1, "c"), ["a", "b"])

    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_get_content_defined(self, mock_find):
        test = xml.etree.ElementTree.Element("test")
        test.text = "d"
        mock_find.return_value = test
        logfunction = print
        self.assertEqual(parser_robobackup_xml.get_content(test, None, logfunction), "d")

    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_get_content_must_be_defined(self, mock_find):
        test = xml.etree.ElementTree.Element("test")
        mock_find.return_value = None
        def errorfunction(s):
            raise RuntimeError("Error")
            return
        with self.assertRaises(RuntimeError):
            parser_robobackup_xml.get_content(test, "test", errorfunction, mustbedefined=True)

    @mock.patch.object(xml.etree.ElementTree.Element, "find", autospec=True)
    def test_get_content_default_value(self, mock_find):
        test = xml.etree.ElementTree.Element("test")
        mock_find.return_value = None
        self.assertEqual(parser_robobackup_xml.get_content(test, "test", _, mustbedefined=True, default_content_if_not_defined="cdc"), "cdc")

class HelperFunctionsInRobobackup(unittest.TestCase):

    @mock.patch("robobackup.call", autospec=True)
    def test_exec_shell_cmd(self, mock_call):
        robobackup.exec_shell_cmd("testcmd")
        mock_call.assert_called_with("testcmd", shell=True)

    def test_check_cmd_results(self):
        commands = ["cmd_a", "cmd_b"]
        results = [0, 1]
        self.assertRaises(RuntimeError, robobackup.check_cmd_results, commands, results)

    def test_check_cmd_results_should_not_raise(self):
        commands = ["cmd_a", "cmd_b"]
        results = [0, 0]
        robobackup.check_cmd_results(commands, results)

    def test_check_cmd_results_should_diff_minerror_not_raise(self):
        commands = ["cmd_a", "cmd_b"]
        results = [0, 1]
        robobackup.check_cmd_results(commands, results, minerror=2)

    def test_check_cmd_results_should_diff_minerror_should_raise(self):
        commands = ["cmd_a", "cmd_b"]
        results = [0, 2]
        self.assertRaises(RuntimeError, robobackup.check_cmd_results, commands, results, minerror=2)

    @mock.patch("os.path.exists", autospec=True)
    def test_create_folder_exists(self, os_path_exits):
        os_path_exits.return_value = True
        robobackup.create_folder("p1")
        os_path_exits.assert_called_with("p1")

    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", autospec=True)
    def test_create_folder_exists(self, os_path_exits, os_makedirs):
        os_path_exits.return_value = False
        os_makedirs.returnValue = True
        robobackup.create_folder("p1")
        os_path_exits.assert_called_with("p1")
        os_makedirs.assert_called_with("p1")

    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", autospec=True)
    def test_create_folder_exists(self, os_path_exits, os_makedirs):
        os_path_exits.return_value = False
        def side_effect(s):
            raise os.error
        os_makedirs.side_effect = side_effect
        self.assertRaises(RuntimeError, robobackup.create_folder, "p1")
        os_path_exits.assert_called_with("p1")
        os_makedirs.assert_called_with("p1")

if __name__ == "__main__":
    unittest.main()
