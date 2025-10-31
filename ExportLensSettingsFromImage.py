#Export tags to a text file

'''
Extract and print tags from front image
Tested with GMS 3.62
'''
import DigitalMicrograph as DM

# Clears the output results window
DM.ClearResults() 


frontImageTags = DM.GetFrontImage().GetTagGroup()

'''
Set up list of tags to go through
'''

TagList = (["Microscope Info:Imaging Mode",
          "Microscope Info:Formatted Indicated Mag",
          "Microscope Info:JEOL:Lenses:CL1",
          "Microscope Info:JEOL:Lenses:CL2",
          "Microscope Info:JEOL:Lenses:CL3",
          "Microscope Info:JEOL:Lenses:CM",
          "Microscope Info:JEOL:Lenses:IL1",
          "Microscope Info:JEOL:Lenses:IL2",
          "Microscope Info:JEOL:Lenses:IL3",
          "Microscope Info:JEOL:Lenses:OL Coarse",
          "Microscope Info:JEOL:Lenses:OL Fine",
          "Microscope Info:JEOL:Lenses:OL Super Fine",
          "Microscope Info:JEOL:Lenses:OM1",
          "Microscope Info:JEOL:Lenses:OM2",
          "Microscope Info:JEOL:Lenses:PL1"
    ])


for x in TagList:
    tagPath = x
    success, val = frontImageTags.GetTagAsString(tagPath)
    if ( success ):
        #print( 'The tag [',tagPath,'] has the value: ', val, sep="" )
        print( tagPath, val, sep="\t" )
    else:
        print( 'The tag [',tagPath,'] was not found or not of valid type.', sep="" )


