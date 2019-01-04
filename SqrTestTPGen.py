from ToolPathGeneration import CompGeo as cg
from ToolPathGeneration import ToolPathTools as tpt
from ToolPathGeneration import HoneycombToolpathTools as htt
import math

def Make_TPGen_Data(material):
    TPGen_Data={}
    
    TPGen_Data['materialname'] = material
    
    TPGen_Data['xdim'] = 5
    TPGen_Data['ydim'] = 7
    TPGen_Data['tiph'] = 0.8 #offset from printing surface
    
    #Computational Geometry Tolerances
    TPGen_Data['disttol'] = 1E-12 #Distance tolerance
    TPGen_Data['angtol'] = 1E-7  #Angular tolerance
    
    #Print parameters
    TPGen_Data['layers'] = 5
    
    materials = []
    materials.append({'material': TPGen_Data['materialname'], 'color': 'b', 'linestyle': '-', 'linewidth': 3, 'alpha': 0.5})
    materials.append({'material': TPGen_Data['materialname']+'slide', 'color': 'r', 'linestyle': ':', 'linewidth': 2, 'alpha': 1})

    TPGen_Data['materials'] = materials
    
    return TPGen_Data

    
def GenerateToolpath(data, target):
    #Unpack data
    
    #Dimensional tolerances for computational geometry
    disttol = data['disttol']
    angtol = data['angtol']    
    
    #line dimensions
    length = data['length'] 
    
    #Print parameters
    tiph = data['tiph']
    materialname = data['materialname']
   
    #-----------------STUFF-----------------------------#

    toolpath3D = []
    toolpath3D.append({'parse':'start'})
    zpos = tiph
    #CONSTRUCTING TOOLPATH
    startpoint = {'X':0 , 'Y':0, 'Z':zpos}
    endpoint = {'X':length , 'Y':0, 'Z':zpos}
    toolpath3D.append({'startpoint':startpoint,'endpoint':endpoint, 'material':materialname})
    toolpath3D.append({'parse':'end'})
    #ADDING in Parsing
    
    #toolpath_parsed = tpt.expandpoints(toolpath3D, ['startpoint','endpoint'], ['X','Y','Z'])
    toolpath_parsed=tpt.parse_endofmotion(toolpath3D, disttol)
    toolpath_parsed=tpt.parse_startofmotion(toolpath_parsed)
    toolpath_parsed=tpt.parse_changemat(toolpath_parsed)
    hierarchylist = ['start','changemat', 'endofmotion', 'endoflayer', 'startofmotion','end']
    toolpath_parsed = tpt.parse_heirarchy(toolpath_parsed, hierarchylist)
    print ('done')
    target[0] = toolpath_parsed




