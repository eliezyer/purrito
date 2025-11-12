"""
Tests for the CatGt wrapper class.
"""

import unittest
import os
from purrito import CatGt


class TestCatGtBasic(unittest.TestCase):
    """Test basic CatGt functionality."""
    
    def test_initialization(self):
        """Test CatGt initialization with basic parameters."""
        catgt = CatGt(basepath="/data/test", run="g0")
        self.assertEqual(catgt.run, "g0")
        self.assertIn("test", catgt.basepath)
        self.assertIsNone(catgt.gate)
        self.assertIsNone(catgt.trigger)
        
    def test_initialization_with_gate_trigger(self):
        """Test initialization with gate and trigger."""
        catgt = CatGt(basepath="/data/test", run="g0", gate=0, trigger=0)
        self.assertEqual(catgt.gate, 0)
        self.assertEqual(catgt.trigger, 0)
        
    def test_basepath_absolute_conversion(self):
        """Test that basepath is converted to absolute path."""
        catgt = CatGt(basepath="relative/path", run="g0")
        self.assertTrue(os.path.isabs(catgt.basepath))


class TestCatGtCommandBuilding(unittest.TestCase):
    """Test command line building functionality."""
    
    def test_basic_command(self):
        """Test building basic command without options."""
        catgt = CatGt(basepath="/data/test", run="g0")
        cmd = catgt.build_command()
        self.assertIn("CatGt", cmd)
        self.assertIn("-dir=", cmd)
        self.assertIn("-run=g0", cmd)
        
    def test_command_with_gate_trigger(self):
        """Test command with gate and trigger."""
        catgt = CatGt(basepath="/data/test", run="g0", gate=0, trigger=0)
        cmd = catgt.build_command()
        self.assertIn("-g=0", cmd)
        self.assertIn("-t=0", cmd)
        
    def test_command_with_custom_catgt_path(self):
        """Test command with custom CatGt executable path."""
        catgt = CatGt(basepath="/data/test", run="g0")
        cmd = catgt.build_command(catgt_path="/usr/local/bin/CatGt")
        self.assertTrue(cmd.startswith("/usr/local/bin/CatGt"))
        
    def test_command_without_gate(self):
        """Test command when only trigger is specified."""
        catgt = CatGt(basepath="/data/test", run="g0", trigger=0)
        cmd = catgt.build_command()
        self.assertNotIn("-g=", cmd)
        self.assertIn("-t=0", cmd)
        
    def test_command_without_trigger(self):
        """Test command when only gate is specified."""
        catgt = CatGt(basepath="/data/test", run="g0", gate=0)
        cmd = catgt.build_command()
        self.assertIn("-g=0", cmd)
        self.assertNotIn("-t=", cmd)


class TestCatGtOptions(unittest.TestCase):
    """Test handling of various option types."""
    
    def test_boolean_options_true(self):
        """Test boolean options that are True."""
        catgt = CatGt(basepath="/data/test", run="g0", ap=True, lf=True)
        cmd = catgt.build_command()
        self.assertIn("-ap", cmd)
        self.assertIn("-lf", cmd)
        
    def test_boolean_options_false(self):
        """Test boolean options that are False (should not appear)."""
        catgt = CatGt(basepath="/data/test", run="g0", ap=False, lf=False)
        cmd = catgt.build_command()
        self.assertNotIn("-ap", cmd)
        self.assertNotIn("-lf", cmd)
        
    def test_string_options(self):
        """Test string value options."""
        catgt = CatGt(basepath="/data/test", run="g0", dest="/output")
        cmd = catgt.build_command()
        self.assertIn("-dest=/output", cmd)
        
    def test_numeric_options(self):
        """Test numeric value options."""
        catgt = CatGt(basepath="/data/test", run="g0", prb=0, prb_fld=1)
        cmd = catgt.build_command()
        self.assertIn("-prb=0", cmd)
        self.assertIn("-prb-fld=1", cmd)
        
    def test_list_options(self):
        """Test list value options (comma-separated)."""
        catgt = CatGt(basepath="/data/test", run="g0", channels=[0, 1, 2, 3])
        cmd = catgt.build_command()
        self.assertIn("-channels=0,1,2,3", cmd)
        
    def test_tuple_options(self):
        """Test tuple value options (comma-separated)."""
        catgt = CatGt(basepath="/data/test", run="g0", range=(100, 200))
        cmd = catgt.build_command()
        self.assertIn("-range=100,200", cmd)
        
    def test_underscore_to_dash_conversion(self):
        """Test that underscores in option names are converted to dashes."""
        catgt = CatGt(basepath="/data/test", run="g0", prb_fld=1, xa_fld=2)
        cmd = catgt.build_command()
        self.assertIn("-prb-fld=1", cmd)
        self.assertIn("-xa-fld=2", cmd)
        
    def test_mixed_options(self):
        """Test command with mixed option types."""
        catgt = CatGt(
            basepath="/data/test",
            run="g0",
            gate=0,
            trigger=0,
            ap=True,
            lf=True,
            dest="/output",
            prb=0,
            channels=[0, 1, 2]
        )
        cmd = catgt.build_command()
        self.assertIn("-ap", cmd)
        self.assertIn("-lf", cmd)
        self.assertIn("-dest=/output", cmd)
        self.assertIn("-prb=0", cmd)
        self.assertIn("-channels=0,1,2", cmd)


class TestCatGtUtilityMethods(unittest.TestCase):
    """Test utility methods."""
    
    def test_get_command_args(self):
        """Test getting command as list of arguments."""
        catgt = CatGt(basepath="/data/test", run="g0", gate=0)
        args = catgt.get_command_args()
        self.assertIsInstance(args, list)
        self.assertEqual(args[0], "CatGt")
        self.assertIn("-dir=/data/test", " ".join(args))
        
    def test_repr(self):
        """Test string representation."""
        catgt = CatGt(basepath="/data/test", run="g0", gate=0, ap=True)
        repr_str = repr(catgt)
        self.assertIn("CatGt", repr_str)
        self.assertIn("basepath", repr_str)
        self.assertIn("run", repr_str)
        
    def test_str(self):
        """Test string conversion."""
        catgt = CatGt(basepath="/data/test", run="g0")
        str_cmd = str(catgt)
        self.assertIn("CatGt", str_cmd)
        self.assertIn("-dir=", str_cmd)
        self.assertIn("-run=g0", str_cmd)


class TestCatGtRealWorldUseCases(unittest.TestCase):
    """Test real-world use cases."""
    
    def test_typical_preprocessing_pipeline(self):
        """Test a typical preprocessing command."""
        catgt = CatGt(
            basepath="/data/neuropixels",
            run="g0",
            gate=0,
            trigger=0,
            ap=True,
            lf=True,
            prb=0,
            prb_fld=1
        )
        cmd = catgt.build_command()
        
        # Verify all expected components are present
        self.assertIn("CatGt", cmd)
        self.assertIn("-dir=", cmd)
        self.assertIn("-run=g0", cmd)
        self.assertIn("-g=0", cmd)
        self.assertIn("-t=0", cmd)
        self.assertIn("-ap", cmd)
        self.assertIn("-lf", cmd)
        self.assertIn("-prb=0", cmd)
        self.assertIn("-prb-fld=1", cmd)
        
    def test_multi_probe_setup(self):
        """Test command for multiple probes."""
        catgt = CatGt(
            basepath="/data/multi_probe",
            run="g0",
            gate=0,
            trigger=0,
            prb=0,
            prb_list=[0, 1, 2]
        )
        cmd = catgt.build_command()
        self.assertIn("-prb-list=0,1,2", cmd)
        
    def test_with_destination_path(self):
        """Test command with custom destination path."""
        catgt = CatGt(
            basepath="/data/input",
            run="g0",
            dest="/data/processed",
            ap=True
        )
        cmd = catgt.build_command()
        self.assertIn("-dest=/data/processed", cmd)


if __name__ == "__main__":
    unittest.main()
