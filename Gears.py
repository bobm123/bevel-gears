#Author-R. Marchese
#Description-Creates a pair of bevel gears. Based on Autodesk sample code by
#Brian Ekins

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# Command inputs
_pressureAngle = adsk.core.DropDownCommandInput.cast(None)
_pressureAngleCustom = adsk.core.ValueCommandInput.cast(None)
_backlash = adsk.core.ValueCommandInput.cast(None)
_module = adsk.core.ValueCommandInput.cast(None)
_numTeeth = adsk.core.StringValueCommandInput.cast(None)
_numTeeth1 = adsk.core.StringValueCommandInput.cast(None)
#_rootFilletRad = adsk.core.ValueCommandInput.cast(None)
_thickness = adsk.core.ValueCommandInput.cast(None)     # TODO: Replace this with face (height of tooth loft)
_holeDiam = adsk.core.ValueCommandInput.cast(None)
_pitchDiam = adsk.core.TextBoxCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        #if _ui:
        #    _ui.messageBox("Running Gears.py")

        cmdDef = _ui.commandDefinitions.itemById('adskXGearPythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition('adskXGearPythonScript', 'XGears', 'Creates a gear component', '') 
        
        # Connect to the command created event.
        onCommandCreated = GearCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class GearCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Verfies that a value command input has a valid expression and returns the 
# value if it does.  Otherwise it returns False.  This works around a 
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make 
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):

    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager
        
        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class GearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()
                
            defaultUnits = des.unitsManager.defaultLengthUnits
                
            # Determine whether to use inches or millimeters as the intial default.
            global _units
            if defaultUnits == 'in' or defaultUnits == 'ft':
                if _ui:
                    _ui.messageBox("Warning: not using metric")
                #_units = 'in'
            #else:
            #    _units = 'mm'

            # First haxxoring of sample gear generator, force _units to mm
            _units = 'mm'
                        
            pressureAngle = '20 deg'
            pressureAngleAttrib = des.attributes.itemByName('SpurGear', 'pressureAngle')
            if pressureAngleAttrib:
                pressureAngle = pressureAngleAttrib.value
            
            pressureAngleCustom = 20 * (math.pi/180.0)
            pressureAngleCustomAttrib = des.attributes.itemByName('SpurGear', 'pressureAngleCustom')
            if pressureAngleCustomAttrib:
                pressureAngleCustom = float(pressureAngleCustomAttrib.value)            

            metricModule = '2.0'
            moduleAttrib = des.attributes.itemByName('SpurGear', 'module')
            if moduleAttrib:
                metricModule = moduleAttrib.value

            backlash = '0.05'
            backlashAttrib = des.attributes.itemByName('SpurGear', 'backlash')
            if backlashAttrib:
                backlash = backlashAttrib.value

            numTeeth = '25'            
            numTeethAttrib = des.attributes.itemByName('SpurGear', 'numTeeth')
            if numTeethAttrib:
                numTeeth = numTeethAttrib.value

            numTeeth1 = '10'            
            numTeeth1Attrib = des.attributes.itemByName('SpurGear', 'numTeeth1')
            if numTeeth1Attrib:
                numTeeth1 = numTeeth1Attrib.value

            #rootFilletRad = str(.05)    # .5 mm
            #rootFilletRadAttrib = des.attributes.itemByName('SpurGear', 'rootFilletRad')
            #if rootFilletRadAttrib:
            #    rootFilletRad = rootFilletRadAttrib.value

            thickness = str(1.0)        # 1 cm 
            thicknessAttrib = des.attributes.itemByName('SpurGear', 'thickness')
            if thicknessAttrib:
                thickness = thicknessAttrib.value
            
            holeDiam = str(0.8)         # 8 mm
            holeDiamAttrib = des.attributes.itemByName('SpurGear', 'holeDiam')
            if holeDiamAttrib:
                holeDiam = holeDiamAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            
            #global _standard, _pressureAngle, _pressureAngleCustom, _diaPitch, _pitch, _module, _numTeeth, _rootFilletRad, _thickness, _holeDiam, _pitchDiam, _backlash, _imgInputEnglish, _imgInputMetric, _errMessage
            global _pressureAngle, _pressureAngleCustom, _pitch, _module, _numTeeth, _numTeeth1, _thickness, _holeDiam, _pitchDiam, _backlash, _errMessage
                       
            _pressureAngle = inputs.addDropDownCommandInput('pressureAngle', 'Pressure Angle', adsk.core.DropDownStyles.TextListDropDownStyle)
            if pressureAngle == '14.5 deg':
                _pressureAngle.listItems.add('14.5 deg', True)
            else:
                _pressureAngle.listItems.add('14.5 deg', False)

            if pressureAngle == '20 deg':
                _pressureAngle.listItems.add('20 deg', True)
            else:
                _pressureAngle.listItems.add('20 deg', False)

            if pressureAngle == '25 deg':
                _pressureAngle.listItems.add('25 deg', True)
            else:
                _pressureAngle.listItems.add('25 deg', False)

            if pressureAngle == 'Custom':
                _pressureAngle.listItems.add('Custom', True)
            else:
                _pressureAngle.listItems.add('Custom', False)

            _pressureAngleCustom = inputs.addValueInput('pressureAngleCustom', 'Custom Angle', 'deg', adsk.core.ValueInput.createByReal(pressureAngleCustom))
            if pressureAngle != 'Custom':
                _pressureAngleCustom.isVisible = False

            _module = inputs.addValueInput('module', 'Module', '', adsk.core.ValueInput.createByReal(float(metricModule)))   
            
            _numTeeth = inputs.addStringValueInput('numTeeth', 'Wheel Teeth', numTeeth)        
            _numTeeth1 = inputs.addStringValueInput('numTeeth1', 'Pinion Teeth', numTeeth1)        

            _backlash = inputs.addValueInput('backlash', 'Backlash', _units, adsk.core.ValueInput.createByReal(float(backlash)))

            #_rootFilletRad = inputs.addValueInput('rootFilletRad', 'Root Fillet Radius', _units, adsk.core.ValueInput.createByReal(float(rootFilletRad)))

            _thickness = inputs.addValueInput('thickness', 'Gear Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _holeDiam = inputs.addValueInput('holeDiam', 'Hole Diameter', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _pitchDiam = inputs.addTextBoxCommandInput('pitchDiam', 'Pitch Diameter', '', 1, True)
            
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True
            
            # Connect to the command related events.
            onExecute = GearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)        
            
            onInputChanged = GearCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)     
            
            onValidateInputs = GearCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)

            onDestroy = GearCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class GearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            #if _standard.selectedItem.name == 'English':
            #    diaPitch = _diaPitch.value            
            #elif _standard.selectedItem.name == 'Metric':
            #    diaPitch = 25.4 / _module.value

            # TODO: replace diaPitch with module in calculations
            #diaPitch = 25.4 / _module.value
            module = _module.value
            
            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            #attribs.add('SpurGear', 'standard', _standard.selectedItem.name)
            attribs.add('SpurGear', 'pressureAngle', _pressureAngle.selectedItem.name)
            attribs.add('SpurGear', 'pressureAngleCustom', str(_pressureAngleCustom.value))
            #attribs.add('SpurGear', 'diaPitch', str(diaPitch))
            attribs.add('SpurGear', 'module', str(module))
            attribs.add('SpurGear', 'numTeeth', str(_numTeeth.value))
            attribs.add('SpurGear', 'numTeeth1', str(_numTeeth1.value))
            #attribs.add('SpurGear', 'rootFilletRad', str(_rootFilletRad.value))
            attribs.add('SpurGear', 'thickness', str(_thickness.value))
            attribs.add('SpurGear', 'holeDiam', str(_holeDiam.value))
            attribs.add('SpurGear', 'backlash', str(_backlash.value))

            # Get the current values.
            if _pressureAngle.selectedItem.name == 'Custom':
                pressureAngle = _pressureAngleCustom.value
            else:
                if _pressureAngle.selectedItem.name == '14.5 deg':
                    pressureAngle = 14.5 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '20 deg':
                    pressureAngle = 20.0 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '25 deg':
                    pressureAngle = 25.0 * (math.pi/180)

            numTeeth = int(_numTeeth.value)
            numTeeth1 = int(_numTeeth1.value)
            #rootFilletRad = _rootFilletRad.value
            thickness = _thickness.value
            holeDiam = _holeDiam.value
            backlash = _backlash.value

            # Create the gears.
            gearComp = drawGearSet(des, module, numTeeth, numTeeth1, thickness, pressureAngle, backlash, holeDiam)
            
            if gearComp:
                desc = 'Gear; Module: ' +  str(module) + '; '
                desc += 'Num Teeth: ' + str(numTeeth) + '; '
                desc += 'Num Teeth1: ' + str(numTeeth1) + '; '
                desc += 'Pressure Angle: ' + str(pressureAngle * (180/math.pi)) + '; '
                desc += 'Backlash: ' + des.unitsManager.formatInternalValue(backlash, _units, True)
                gearComp.description = desc

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
        
# Event handler for the inputChanged event.
class GearCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            
            global _units

            module = None
            result = getCommandInputValue(_module, '')
            if result[0]:
                module = result[1]

            if not module == None:
                if _numTeeth.value.isdigit(): 
                    numTeeth = int(_numTeeth.value)
                    pitchDia = numTeeth * module

                    # The pitch dia has been calculated in mm, but this expects cm as the input units.
                    des = adsk.fusion.Design.cast(_app.activeProduct)
                    pitchDiaText = des.unitsManager.formatInternalValue(pitchDia / 10, _units, True)
                    _pitchDiam.text = pitchDiaText
                else:
                    _pitchDiam.text = ''                    

                # TODO:  _pitchDiam.text should show both values
                if _numTeeth1.value.isdigit(): 
                    numTeeth1 = int(_numTeeth1.value)
            else:
                _pitchDiam.text = ''

            if changedInput.id == 'pressureAngle':
                if _pressureAngle.selectedItem.name == 'Custom':
                    _pressureAngleCustom.isVisible = True
                else:
                    _pressureAngleCustom.isVisible = False                    
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
        
# Event handler for the validateInputs event.
class GearCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            
            _errMessage.text = ''

            # Verify that at least 4 teath are specified.
            if not _numTeeth.value.isdigit():
                _errMessage.text = 'The number of teeth must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:    
                numTeeth = int(_numTeeth.value)
            
            if numTeeth < 4:
                _errMessage.text = 'The number of teeth must be 4 or more.'
                eventArgs.areInputsValid = False
                return

            # Do the same for the pinion.
            if not _numTeeth1.value.isdigit():
                _errMessage.text = 'The number of teeth must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:    
                numTeeth1 = int(_numTeeth1.value)
            
            if numTeeth1 < 4:
                _errMessage.text = 'The number of teeth must be 4 or more.'
                eventArgs.areInputsValid = False
                return

            # With only metric standard, this confusing block of code
            # can be replaced with 
            #   pitchDia = numTeeth * module 
            result = getCommandInputValue(_module, '')
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                diaPitch = 25.4 / result[1]

            diametralPitch = diaPitch / 2.54
            pitchDia = numTeeth / diametralPitch
            # pitchDia is the key thing we need from number of teeth
            # and tooth size either by means of pitchDiameter or with
            # metric, the module
            
            # Handles situation where dedendum is outside the root circle
            # TODO: replace calulation with equivilant Z*module. 
            if (diametralPitch < (20 *(math.pi/180))-0.000001):
                dedendum = 1.157 / diametralPitch
            else:
                circularPitch = math.pi / diametralPitch
                if circularPitch >= 20:
                    dedendum = 1.25 / diametralPitch
                else:
                    dedendum = (1.2 / diametralPitch) + (.002 * 2.54)                

            rootDia = pitchDia - (2 * dedendum)        
                    
            if _pressureAngle.selectedItem.name == 'Custom':
                pressureAngle = _pressureAngleCustom.value
            else:
                if _pressureAngle.selectedItem.name == '14.5 deg':
                    pressureAngle = 14.5 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '20 deg':
                    pressureAngle = 20.0 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '25 deg':
                    pressureAngle = 25.0 * (math.pi/180)
            baseCircleDia = pitchDia * math.cos(pressureAngle)
            baseCircleCircumference = 2 * math.pi * (baseCircleDia / 2) 

            des = adsk.fusion.Design.cast(_app.activeProduct)

            result = getCommandInputValue(_holeDiam, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                holeDiam = result[1]
                           
            if holeDiam >= (rootDia - 0.01):
                _errMessage.text = 'The center hole diameter is too large.  It must be less than ' + des.unitsManager.formatInternalValue(rootDia - 0.01, _units, True)
                eventArgs.areInputsValid = False
                return

            #TODO: Add check for backlash here

            #toothThickness = baseCircleCircumference / (numTeeth * 2)
            #if _rootFilletRad.value > toothThickness * .4:
            #    _errMessage.text = 'The root fillet radius is too large.  It must be less than ' + des.unitsManager.formatInternalValue(toothThickness * .4, _units, True)
            #    eventArgs.areInputsValid = False
            #    return
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Calculate points along an involute curve.
def involutePoint(baseCircleRadius, distFromCenterToInvolutePoint):
    try:
        # Calculate the other side of the right-angle triangle defined by the base circle and the current distance radius.
        # This is also the length of the involute chord as it comes off of the base circle.
        triangleSide = math.sqrt(math.pow(distFromCenterToInvolutePoint,2) - math.pow(baseCircleRadius,2)) 
        
        # Calculate the angle of the involute.
        alpha = triangleSide / baseCircleRadius

        # Calculate the angle where the current involute point is.
        theta = alpha - math.acos(baseCircleRadius / distFromCenterToInvolutePoint)

        # Calculate the coordinates of the involute point.    
        x = distFromCenterToInvolutePoint * math.cos(theta)
        y = distFromCenterToInvolutePoint * math.sin(theta)

        # Create a point to return.        
        return adsk.core.Point3D.create(x, y, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Draws a tooth profile on the given plane
def drawToothProfile(toothSketch, module, numTeeth, pressureAngle, backlash, ratio):
    '''
    For proper tooth shape in a bevel gear, R0 should be larger than value given by 
    spur gear calculation (m*z/2). Using Tredgold's approximation, reference pitch
    radius is the slant height of the back cone: 
        https://en.wikipedia.org/wiki/List_of_gear_nomenclature#Back_cone
    r0 = m*z/2;          // Reference pitch radius by tooth and module
    R0 = r0/sin(atan(ratio));   // Tredgold's approximation
    Zi = 2*R0/m;                // tooth count of the imaginary spur gear
    Rb = R0*cos(alpha); // Base pitch radius
    Ra = R0+m;          // Addendum circle radius
    Rd = R0-(m+c*m);    // Dedendum circle radius
    '''

    # Compute the various values for a gear.
    pitchDia = numTeeth * module
    r0 = numTeeth * module
    bca = module * numTeeth * ratio     
    R0 = math.sqrt(bca*bca + pitchDia*pitchDia) / 2
    Zi = 2*R0/module

    pitchDia = R0 * 2
    #if (1/module < (20 *(math.pi/180))-0.000001):
    #    dedendum = 1.157 * module
    #else:
    #    circularPitch = math.pi * module
    #    if circularPitch >= 20:
    #        dedendum = 1.25 * module
    #    else:
    #        dedendum = (1.2 * module) + (.002 * 2.54)
    dedendum = module * 1.157   #TODO: Add clearance to user inputs

    rootDia = pitchDia - (2 * dedendum)
    baseCircleDia = pitchDia * math.cos(pressureAngle)
    outsideDia = pitchDia + 2 * module
    # Compute the various values for a gear.

    # Calculate points along the involute curve.
    involutePointCount = 15 
    involutePoints = []
    involuteSize = (outsideDia - rootDia) / 2.0
    for i in range(0, involutePointCount):
        #involuteIntersectionRadius = (baseCircleDia / 2.0) + ((involuteSize / (involutePointCount - 1)) * i)
        involuteIntersectionRadius = (rootDia / 2.0) + ((involuteSize / (involutePointCount - 1)) * i)
        if involuteIntersectionRadius >= baseCircleDia / 2.0:
            newPoint = involutePoint(baseCircleDia / 2.0, involuteIntersectionRadius)
            involutePoints.append(newPoint)
        
    # Get the point along the tooth that's at the pitch diameter and then
    # calculate the angle to that point.
    pitchInvolutePoint = involutePoint(baseCircleDia / 2.0, pitchDia / 2.0)
    pitchPointAngle = math.atan(pitchInvolutePoint.y / pitchInvolutePoint.x)

    # Determine the angle defined by the tooth thickness as measured at
    # the pitch diameter circle.
    toothThicknessAngle = (2 * math.pi) / (2 * Zi)
    
    # Determine the angle needed for the specified backlash.
    backlashAngle = (backlash / (pitchDia / 2.0)) * .25
    
    # Determine the angle to rotate the curve.
    rotateAngle = -((toothThicknessAngle/2) + pitchPointAngle - backlashAngle)
    
    # Rotate the involute so the middle of the tooth lies on the x axis.
    cosAngle = math.cos(rotateAngle)
    sinAngle = math.sin(rotateAngle)
    for i, iPoint in enumerate(involutePoints):
        newX = iPoint.x * cosAngle - iPoint.y * sinAngle
        newY = iPoint.x * sinAngle + iPoint.y * cosAngle
        involutePoints[i] = adsk.core.Point3D.create(newX, newY, 0)

    # Create a new set of points with a negated y.  This effectively mirrors the original
    # points about the X axis.
    involute2Points = []
    for iPoint in involutePoints:
        involute2Points.append(adsk.core.Point3D.create(iPoint.x, -iPoint.y, 0))

    #
    curve1Angle0 = math.atan(involutePoints[0].y / involutePoints[0].x)
    curve2Angle0 = math.atan(involute2Points[0].y / involute2Points[0].x)

    toothSketch.isComputeDeferred = True
    
    # Create and load an object collection with the points.
    pointSet = adsk.core.ObjectCollection.create()
    for iPoint in involutePoints:
        pointSet.add(iPoint)

    # Create the first spline.
    spline1 = toothSketch.sketchCurves.sketchFittedSplines.add(pointSet)

    # Add the involute points for the second spline to an ObjectCollection.
    pointSet = adsk.core.ObjectCollection.create()
    for iPoint in involute2Points:
        pointSet.add(iPoint)

    # Create the second spline.
    spline2 = toothSketch.sketchCurves.sketchFittedSplines.add(pointSet)

    # Draw the arc for the top of the tooth.
    midPoint = adsk.core.Point3D.create((outsideDia / 2), 0, 0)
    toothSketch.sketchCurves.sketchArcs.addByThreePoints(spline1.endSketchPoint, midPoint, spline2.endSketchPoint)     

    # Check to see if involute goes down to the root or not.  If not, then
    # create lines to connect the involute to the root.
    if( baseCircleDia < rootDia ):
        toothSketch.sketchCurves.sketchLines.addByTwoPoints(spline2.startSketchPoint, spline1.startSketchPoint)
        profilePoint = involutePoints[0]
    else:
        rootPoint1 = adsk.core.Point3D.create((rootDia / 2 - 0.001) * math.cos(curve1Angle0 ), (rootDia / 2) * math.sin(curve1Angle0), 0)
        line1 = toothSketch.sketchCurves.sketchLines.addByTwoPoints(rootPoint1, spline1.startSketchPoint)

        rootPoint2 = adsk.core.Point3D.create((rootDia / 2 - 0.001) * math.cos(curve2Angle0), (rootDia / 2) * math.sin(curve2Angle0), 0)
        line2 = toothSketch.sketchCurves.sketchLines.addByTwoPoints(rootPoint2, spline2.startSketchPoint)

        baseLine = toothSketch.sketchCurves.sketchLines.addByTwoPoints(line1.startSketchPoint, line2.startSketchPoint)

        # Make the lines tangent to the spline so the root fillet will behave correctly.            
        line1.isFixed = True
        line2.isFixed = True
        toothSketch.geometricConstraints.addTangent(spline1, line1)
        toothSketch.geometricConstraints.addTangent(spline2, line2)

        profilePoint = rootPoint1
    
    toothSketch.isComputeDeferred = False

    return profilePoint


# Builds a metric gear tooth.
def drawGearSet(design, module, numTeeth, numTeeth1, thickness, pressureAngle, backlash, holeDiam):
    try:
        # The module is specified in mm but everthing
        # here expects all distances to be in centimeters, so convert
        # for the gear creation.
        module = module / 10

        ###### Compute the various values for a gear.
        pitchDia = numTeeth * module
        pitchDia1 = numTeeth1 * module

        #addendum = module
        if (1/module < (20 *(math.pi/180))-0.000001):
            dedendum = 1.157 * module
        else:
            circularPitch = math.pi * module
            if circularPitch >= 20:
                dedendum = 1.25 * module
            else:
                dedendum = (1.2 * module) + (.002 * 2.54)

        rootDia = pitchDia - (2 * dedendum)
        baseCircleDia = pitchDia * math.cos(pressureAngle)
        outsideDia = (numTeeth + 2) * module

        ###### Create a new component by creating an occurrence.
        occs = design.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)        
        newComp = adsk.fusion.Component.cast(newOcc.component)

        ###### Create a new sketch for the cross section of the gears
        sketches = newComp.sketches
        xzPlane = newComp.xZConstructionPlane
        crossSectionSketch = sketches.add(xzPlane)

        # A rectangle defining the gears geometry based on their ratio
        coneCenter = adsk.core.Point3D.create(0, -pitchDia1/2, 0)
        pitchTangent = adsk.core.Point3D.create(pitchDia/2, 0, 0)
        pinionCenter = adsk.core.Point3D.create(pitchDia/2, -pitchDia1/2, 0)
        wheelCenter = adsk.core.Point3D.create(0,0,0)

        coneCenterSP = crossSectionSketch.sketchPoints.add(coneCenter)

        lines = crossSectionSketch.sketchCurves.sketchLines
        coneTangentLine = lines.addByTwoPoints(pitchTangent, coneCenter)
        wheelAxis = lines.addByTwoPoints(wheelCenter, coneCenter)       # for creating rotations later
        wheelBase = lines.addByTwoPoints(wheelCenter, pitchTangent)     # not sure this is needed
        pinionAxis = lines.addByTwoPoints(pinionCenter, coneCenter)     # for creating rotations later
        pinionBase = lines.addByTwoPoints(pinionCenter, pitchTangent)   # not sure this is needed

        coneTangentLine.isConstruction = True
        coneTangentLine.isFixed = True
        wheelBase.isConstruction = True
        wheelBase.isFixed = True
        pinionBase.isConstruction = True
        pinionBase.isFixed = True

        # Make a plane at an angle for the tooth profile using the gear's back cone
        ratio = numTeeth/numTeeth1
        backConeHeight = module * numTeeth * ratio /2

        # actually extended by 2x so plane's origin on z-axis
        backApex = adsk.core.Point3D.create(-pitchDia/2,backConeHeight*2,0)
        backAngle = math.atan(pitchDia / (backConeHeight*2))
        wheelBackCone = lines.addByTwoPoints(backApex, pitchTangent)
        wheelBackCone.isConstruction = True
        wheelBackCone.isFixed = True
        planes = newComp.constructionPlanes
        planeInput = planes.createInput()
        planeInput.setByAngle(wheelBackCone, adsk.core.ValueInput.createByReal(0.0), None)
        toothPlane = planes.add(planeInput)

        # Add a sketch for the tooth points defined above 
        toothSketch = sketches.add(toothPlane)

        # Sketch to tooth profile, returns a point at the tooth's root
        rootPoint = drawToothProfile(toothSketch, module, numTeeth, pressureAngle, backlash, ratio)

        # Add some projected points from the tooth profile for the root cone
        a = backConeHeight-rootPoint.x*math.cos(backAngle)
        wheelConeA = adsk.core.Point3D.create(0,a,0)
        b = pitchDia/2 - a*math.tan(backAngle)
        b = math.sqrt(b*b+rootPoint.y*rootPoint.y)
        wheelConeB = adsk.core.Point3D.create(b,a,0)
        wheelAxisExt = lines.addByTwoPoints(wheelCenter, wheelConeA)
        wheelConeBase = lines.addByTwoPoints(wheelConeA, wheelConeB)
        wheelConeSlant = lines.addByTwoPoints(wheelConeB, coneCenter)

        ##### Loft the tooth profile to the cone center and make a new component
        wheelToothProfile = toothSketch.profiles.item(0)
        loftFeats = newComp.features.loftFeatures
        loftInput = loftFeats.createInput(adsk.fusion.FeatureOperations.NewComponentFeatureOperation)
        loftSectionsObj = loftInput.loftSections
        loftSectionsObj.add(wheelToothProfile)
        coneCenterSP = crossSectionSketch.sketchPoints.add(coneCenter)
        loftSectionsObj.add(coneCenterSP)
        wheelLoft = loftFeats.add(loftInput)

        wheelOcc = newComp.occurrences.item(0)
        wheelComp = adsk.fusion.Component.cast(wheelOcc.component)
        wheelComp.name = f'{numTeeth} Tooth'

        ##### Add construction plane for the pinion teeth at an angle based on gear ratio
        ratio = numTeeth1/numTeeth
        backConeHeight = module * numTeeth1 * ratio /2
        
        # Make a plane at an angle for the tooth profile using the gear's back cone
        # actually extended by 2x so plane origin's on z-axis
        backApex = adsk.core.Point3D.create(pitchDia/2+backConeHeight*2,-pitchDia1,0)
        backAngle = math.atan(pitchDia1 / (backConeHeight*2))
        pinionBackCone = lines.addByTwoPoints(backApex, pitchTangent)
        pinionBackCone.isConstruction = True
        pinionBackCone.isFixed = True
        planes = newComp.constructionPlanes
        planeInput = planes.createInput()
        planeInput.setByAngle(pinionBackCone, adsk.core.ValueInput.createByReal(0.0), None)
        toothPlane = planes.add(planeInput)

        # Add a sketch for the tooth points defined above 
        toothSketch = sketches.add(toothPlane)

        # Sketch to tooth profile, returns a point at the tooth's root
        rootPoint = drawToothProfile(toothSketch, module, numTeeth1, pressureAngle, backlash, ratio)

        # Add some projected points from the tooth profile for the root cone
        a = backConeHeight-rootPoint.x*math.cos(backAngle)
        pinionConeA = adsk.core.Point3D.create(pitchDia/2+a,-pitchDia1/2,0)
        b = pitchDia1/2 - a*math.tan(backAngle)
        b = math.sqrt(b*b+rootPoint.y*rootPoint.y)
        pinionConeB = adsk.core.Point3D.create(pitchDia/2+a,b-pitchDia1/2,0)
        pinionAxisExt = lines.addByTwoPoints(pinionCenter, pinionConeA)
        pinionConeBase = lines.addByTwoPoints(pinionConeA, pinionConeB)
        pinionConeSlant = lines.addByTwoPoints(pinionConeB, coneCenter)

        ##### Loft the tooth profile to the cone center and make a new component
        pinionToothProfile = toothSketch.profiles.item(0)
        loftFeats = newComp.features.loftFeatures
        loftInput = loftFeats.createInput(adsk.fusion.FeatureOperations.NewComponentFeatureOperation)
        loftSectionsObj = loftInput.loftSections
        loftSectionsObj.add(pinionToothProfile)
        coneCenterSP = crossSectionSketch.sketchPoints.add(coneCenter)
        loftSectionsObj.add(coneCenterSP)
        pinionLoft = loftFeats.add(loftInput)

        pinionOcc = newComp.occurrences.item(1)
        pinionComp = adsk.fusion.Component.cast(pinionOcc.component)
        pinionComp.name = f'{numTeeth1} Tooth'

        # Add some lines to the cross section sketch for trimming the teeth
        wheelFace = SplitLineAt(wheelConeSlant, thickness)
        pinionFace = SplitLineAt(pinionConeSlant, thickness)
        lines.addByTwoPoints(wheelFace, pinionFace)

        newWpt = adsk.core.Point3D.create(0, wheelFace.y, 0)
        wheelAxis.split(newWpt)
        lines.addByTwoPoints(wheelFace, newWpt)

        newPpt = adsk.core.Point3D.create(pinionFace.x, pinionCenter.y, 0)
        pinionAxis.split(newPpt)
        lines.addByTwoPoints(pinionFace, newPpt)

        ##### Remove the excess material near the apex of each tooth
        # Can use all the sketch profiles for the cut operation. While iterating
        # over all the profiles on the criss section sketch can look for the
        # the profiles to revolve for the root cones for the wheel and pinion 
        crossSectionProfiles = adsk.core.ObjectCollection.create()
        centX = []
        centY = []
        for p in crossSectionSketch.profiles:
            crossSectionProfiles.add(p)
            areaProps = p.areaProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
            centX.append(areaProps.centroid.x)
            centY.append(areaProps.centroid.y)

        # Find the profile to rotate using the centroids
        wIndex = centY.index(max(centY))     # the lowest y-axis (max val since y runs negative)
        pIndex = centX.index(max(centX))     # the greatest x-value
        #_ui.messageBox(f'wheel: {w}, pinion {p} ')
        wheelRootCone = crossSectionSketch.profiles.item(wIndex)
        pinionRootCode = crossSectionSketch.profiles.item(pIndex)

        revolves0 = wheelComp.features.revolveFeatures
        extCutInput = revolves0.createInput(crossSectionProfiles, wheelAxis, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extCutInput.setAngleExtent(True, adsk.core.ValueInput.createByReal(2*math.pi))
        extCutInput.participantBodies = [wheelLoft.bodies.item(0)]
        ext = revolves0.add(extCutInput)

        revolves1 = pinionComp.features.revolveFeatures
        extCutInput = revolves1.createInput(crossSectionProfiles, pinionAxis, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extCutInput.setAngleExtent(True, adsk.core.ValueInput.createByReal(2*math.pi))
        extCutInput.participantBodies = [pinionLoft.bodies.item(0)]
        ext = revolves1.add(extCutInput)

        ##### Create Circular patters for the teeth
        # Create input entities for circular pattern (wheel)
        inputEntites = adsk.core.ObjectCollection.create()
        inputEntites.add(wheelComp.bRepBodies.item(0))

        # Create the input for circular pattern
        circularFeats = wheelComp.features.circularPatternFeatures
        circularFeatInput = circularFeats.createInput(inputEntites, wheelAxis)
        circularFeatInput.quantity = adsk.core.ValueInput.createByReal(numTeeth)
        circularFeatInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')
        circularFeatInput.isSymmetric = False

        # Create the circular pattern of wheel teeth
        circularFeat = circularFeats.add(circularFeatInput)

        # Create input entities for circular pattern (pinion)
        inputEntites = adsk.core.ObjectCollection.create()
        inputEntites.add(pinionComp.bRepBodies.item(0))

        # Create the input for circular pattern
        circularFeats = pinionComp.features.circularPatternFeatures
        circularFeatInput = circularFeats.createInput(inputEntites, pinionAxis)
        circularFeatInput.quantity = adsk.core.ValueInput.createByReal(numTeeth1)
        circularFeatInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')
        circularFeatInput.isSymmetric = False

        # Create the circular pattern of pinion teeth
        circularFeat = circularFeats.add(circularFeatInput)

        ##### Revolve the root cones
        extBodyInput = revolves0.createInput(wheelRootCone, wheelAxis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extBodyInput.setAngleExtent(True, adsk.core.ValueInput.createByReal(2*math.pi))
        ext = revolves0.add(extBodyInput)
        extBodyInput = revolves1.createInput(pinionRootCode, pinionAxis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extBodyInput.setAngleExtent(True, adsk.core.ValueInput.createByReal(2*math.pi))
        ext = revolves1.add(extBodyInput)

        #### Drill holes for the shafts
        wheelSketches = wheelComp.sketches
        rootConeBody = wheelComp.bRepBodies.item(wheelComp.bRepBodies.count-1)
        planarFaces = []
        for i,face in enumerate(rootConeBody.faces):
            #_ui.messageBox(f'face {i} type  {face.geometry.surfaceType}')
            if 0 == face.geometry.surfaceType:
                planarFaces.append(rootConeBody.faces.item(i))

        wheelSketch = wheelSketches.add(planarFaces[0])
        wheelSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), holeDiam/2.0)
        extrudes = wheelComp.features.extrudeFeatures
        extInput = extrudes.createInput(wheelSketch.profiles.item(1), adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput.participantBodies = [rootConeBody]
        extent_toentity = adsk.fusion.ToEntityExtentDefinition.create(planarFaces[1], True)
        extInput.setOneSideExtent(extent_toentity, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        ext = extrudes.add(extInput)

        pinionSketches = pinionComp.sketches
        rootConeBody = pinionComp.bRepBodies.item(pinionComp.bRepBodies.count-1)
        planarFaces = []
        for i,face in enumerate(rootConeBody.faces):
            #_ui.messageBox(f'face {i} type  {face.geometry.surfaceType}')
            if 0 == face.geometry.surfaceType:
                planarFaces.append(rootConeBody.faces.item(i))

        pinionSketch = pinionSketches.add(planarFaces[1])
        pinionSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(-pitchDia1/2,0,0), holeDiam/2.0)
        extrudes = pinionComp.features.extrudeFeatures
        extInput = extrudes.createInput(pinionSketch.profiles.item(1), adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput.participantBodies = [rootConeBody]
        extent_toentity = adsk.fusion.ToEntityExtentDefinition.create(planarFaces[0], True)
        extInput.setOneSideExtent(extent_toentity, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        ext = extrudes.add(extInput)

        # TODO: Udpdate this as new features are added so they can be squashed on the timeline
        lastGearFeature = ext.timelineObject.index

        # Group everything used to create the gear in the timeline.
        timelineGroups = design.timeline.timelineGroups
        newOccIndex = newOcc.timelineObject.index
        timelineGroup = timelineGroups.add(newOccIndex, lastGearFeature)
        timelineGroup.name = 'BevelGears'
        
        # Add an attribute to the component with all of the input values.  This might 
        # be used in the future to be able to edit the gear. TODO: Add a few bevel gear
        # specific parameters here
        gearValues = {}
        gearValues['module'] = str(module)
        gearValues['numTeeth'] = str(numTeeth)
        gearValues['numTeeth1'] = str(numTeeth1)
        gearValues['thickness'] = str(thickness)
        gearValues['pressureAngle'] = str(pressureAngle)
        gearValues['holeDiam'] = str(holeDiam)
        gearValues['backlash'] = str(backlash)
        attrib = newComp.attributes.add('BevelGear', 'Values',str(gearValues))
        
        newComp.name = f'{numTeeth}/{numTeeth1} Bevel Gears'
        return newComp

    except Exception as error:
        _ui.messageBox("drawGearSet Failed : " + str(error)) 
        return None


def SplitLineAt(line, distance):
    start = line.startSketchPoint.geometry
    end = line.endSketchPoint.geometry
    length = line.length
    xs = start.x + distance * (end.x - start.x) / length
    ys = start.y + distance * (end.y - start.y) / length
    zs = start.z + distance * (end.z - start.z) / length
    
    #_ui.messageBox(f'splitting ({start.x} {start.y} {start.z}) to ({end.x} {end.y} {end.z}) at ({xs} {ys} {zs}) {distance} {length}') 
    split_pt = adsk.core.Point3D.create(xs, ys, zs)
    line.split(split_pt)

    return(split_pt)
