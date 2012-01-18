#!/usr/bin/env python3

import sys, os, unittest, logging

# Extend PYTHONPATH with local 'lib' folder
jasyroot = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]), os.pardir, os.pardir, "lib"))
sys.path.insert(0, jasyroot)

import jasy.core.Permutation as Permutation

import jasy.js.parse.Parser as Parser
import jasy.js.parse.ScopeScanner as ScopeScanner
import jasy.js.output.Compressor as Compressor
import jasy.js.clean.Permutate as Permutate


class Tests(unittest.TestCase):

    def process(self, code, contextId=""):
        node = Parser.parse(code)
        permutation = Permutation.Permutation({
            'debug': False,
            'legacy': True,
            'engine': 'webkit',
            'version': 3,
            'fullversion': 3.11
        })
        Permutate.patch(node, permutation)
        return Compressor.Compressor().compress(node)    
    
    
    def test_get(self):
        self.assertEqual(self.process(
            'var engine = core.Env.getValue("engine");'),
            'var engine="webkit";'
        )

    def test_if_isset(self):
        self.assertEqual(self.process(
            '''
            if (core.Env.isSet("debug", true)) {
                var x = 1;
            }
            '''),
            'if(false){var x=1}'
        )        

    def test_isset_bool_false(self):
        self.assertEqual(self.process(
            'var debug = core.Env.isSet("debug", true);'),
            'var debug=false;'
        )             
        
    def test_isset_bool_shorthand_false(self):
        self.assertEqual(self.process(
            'var debug = core.Env.isSet("debug");'),
            'var debug=false;'
        )
        
    def test_isset_bool_true(self):
        self.assertEqual(self.process(
            'var legacy = core.Env.isSet("legacy", true);'),
            'var legacy=true;'
        )
        
    def test_isset_bool_shorthand_true(self):
        self.assertEqual(self.process(
            'var legacy = core.Env.isSet("legacy");'),
            'var legacy=true;'
        )             

    def test_isset_typediff(self):
        self.assertEqual(self.process(
            'var legacy = core.Env.isSet("legacy", "foo");'),
            'var legacy=false;'
        )

    def test_isset_lookup(self):
        self.assertEqual(self.process(
            'var legacy = core.Env.isSet("legacy", x);'),
            'var legacy=core.Env.isSet("legacy",x);'
        )        
        
    def test_isset_int_true(self):
        self.assertEqual(self.process(
            'var recent = core.Env.isSet("version", 3);'),
            'var recent=true;'
        )             

    def test_isset_int_false(self):
        self.assertEqual(self.process(
            'var recent = core.Env.isSet("version", 5);'),
            'var recent=false;'
        )

    def test_isset_float_true(self):
        self.assertEqual(self.process(
            'var buggy = core.Env.isSet("fullversion", 3.11);'),
            'var buggy=true;'
        )

    def test_isset_float_false(self):
        self.assertEqual(self.process(
            'var buggy = core.Env.isSet("fullversion", 3.2);'),
            'var buggy=false;'
        )           
        
    def test_isset_str_single(self):
        self.assertEqual(self.process(
            'var modern = core.Env.isSet("engine", "webkit");'),
            'var modern=true;'
        )
        
    def test_isset_str_multi(self):
        self.assertEqual(self.process(
            'var modern = core.Env.isSet("engine", "gecko|webkit");'),
            'var modern=true;'
        )
        
    def test_isset_str_multilong(self):
        self.assertEqual(self.process(
            'var modern = core.Env.isSet("engine", "gecko|webkitbrowser");'),
            'var modern=false;'
        )            

    def test_select(self):
        self.assertEqual(self.process(
            '''
            var prefix = core.Env.select("engine", {
              webkit: "Webkit",
              gecko: "Moz",
              trident: "ms"
            });
            '''),
            'var prefix="Webkit";'
        )

    def test_select_notfound(self):
        self.assertEqual(self.process(
            '''
            var prefix = core.Env.select("engine", {
              gecko: "Moz",
              trident: "ms"
            });            
            '''),
            'var prefix=core.Env.select("engine",{gecko:"Moz",trident:"ms"});'
        )        
        
    def test_select_default(self):
        self.assertEqual(self.process(
            '''
            var prefix = core.Env.select("engine", {
              gecko: "Moz",
              trident: "ms",
              "default": ""
            });            
            '''),
            'var prefix="";'
        )

    def test_select_multi(self):
        self.assertEqual(self.process(
            '''
            var prefix = core.Env.select("engine", {
              "webkit|khtml": "Webkit",
              trident: "ms",
            });            
            '''),
            'var prefix="Webkit";'
        )             


    
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.ERROR)
    suite = unittest.TestLoader().loadTestsFromTestCase(Tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
    