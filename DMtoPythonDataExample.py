import DigitalMicrograph as DM

#It would be good if there was something like this, but
# it appears there isnt
#DM.GetDirectoryDialog( "Select folder" , "" , folder )

#So this long winded mess is what I've got
#DM script to ask for the folder
# Then stick it in a tag, as dmScript can't return directly
# to Python??? 

Dir = 'dummy'
Dir2 = 'dummy'

dmScript = 'string folder , outputFolder' + '\n'
dmScript += 'if ( !GetDirectoryDialog( "Select folder" , "" , folder ) ) ' + '\n'
dmScript += '     Result(folder)' + '\n'
dmScript += '     string Dir = folder' + '\n'
dmScript += '     string Dir2 = folder' + '\n'
dmScript += '     TagGroup tg = GetPersistentTagGroup( ) ' + '\n'
dmScript += '     tg.TagGroupSetTagAsString( "DM2Python String", folder )' + '\n'

#Execute the script
DM.ExecuteScriptString( dmScript )

#Get the selection data into python
TGp = DM.GetPersistentTagGroup()
returnVal, val = TGp.GetTagAsText('DM2Python String')

print(returnVal)
print(val)

#val is the python string containing the folder