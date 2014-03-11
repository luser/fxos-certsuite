from webapi_tests import MinimalTestCase

class TestProximity(MinimalTestCase):
    def tearDown(self):
        self.marionette.execute_script("""
        window.removeEventListener('devicelight', window.wrappedJSObject.prox_function);
        """)
        MinimalTestCase.tearDown(self)
    def test_proximity_change(self):
        self.instruct("Ensure the phone is unlocked and held in your hand, perpendicular to the floor")
        # set up listener to store changes in an object
        # NOTE: use wrappedJSObject to access non-standard properties of window
        script = """
        window.wrappedJSObject.proximityStates = [];
        window.wrappedJSObject.prox_function = function(event){
                                  console.log("proximity event" + event);
                                  window.wrappedJSObject.proximityStates.push(event.toString());
                                };
        window.addEventListener('devicelight', window.wrappedJSObject.prox_function);
        """
        self.marionette.execute_script(script)
        self.instruct("Move your hand in front of the phone and hit OK when the screen darkens")
        proximity_values = self.marionette.execute_script("return window.wrappedJSObject.proximityStates")
        self.assertNotEqual(0, len(proximity_values))
