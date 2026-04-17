// Tilts reporter
// Reports TX angles into output window to be saved

////////////////////////////////////////////////////////////////////////////////////////

//Function to get tilt angle and report
void PerformBatchAction( image img, string fname )
{
	//result("\n running Batch Action")
	TagGroup tg = img.ImageGetTagGroup()
	TagGroup infoTG
	tg.TagGroupGetTagAsTagGroup("Microscope Info", infoTG )
	TagGroup stageTG
	infoTG.TagGroupGetTagAsTagGroup( "Stage Position", stageTG )
	number TiltX
	string whatalph = "Stage Alpha"
	stageTG.TagGroupGetTagAsFloat( whatalph, TiltX )
	result("\n")
	result(TiltX)
}


////////////////////////////////////////////////////////////////////////////////////////
//Supporting functions
 
// Function converts a string to lower-case characters

string ToLowerCase( string in )
{
 string out = ""
 for( number c = 0 ; c < len( in ) ; c++ )
 {
         string letter = mid( in , c , 1 )
         number n = asc( letter )
         if ( ( n > 64 ) && ( n < 91 ) )        letter = chr( n + 32 )
         out += letter
         }        

 return out

}
 
// Function to create a list of file entries with full path
TagGroup CreateFileList( string folder, number inclSubFolder )
{
 TagGroup filesTG = GetFilesInDirectory( folder , 1 )                        // 1 = Get files, 2 = Get folders, 3 = Get both
 TagGroup fileList = NewTagList()

 for (number i = 0; i < filesTG.TagGroupCountTags() ; i++ )
 {
         TagGroup entryTG
         if ( filesTG.TagGroupGetIndexedTagAsTagGroup( i , entryTG ) )
         {
                 string fileName
                 if ( entryTG.TagGroupGetTagAsString( "Name" , fileName ) )
                 {
                         filelist.TagGroupInsertTagAsString( fileList.TagGroupCountTags() , PathConcatenate( folder , fileName ) )
                 }
         }
 }

 

 if ( inclSubFolder )
 {
         TagGroup allFolders = GetFilesInDirectory( folder, 2 )
         number nFolders = allFolders.TagGroupCountTags()
         for ( number i = 0; i < nFolders; i++ )
         {
                 string sfolder
                 TagGroup entry
                 allFolders.TagGroupgetIndexedTagAsTagGroup( i , entry )
                 entry.TagGroupGetTagAsString( "Name" , sfolder )
                 sfolder = StringToLower( sfolder )
                 TagGroup SubList = CreateFileList( PathConcatenate( folder , sfolder ) , inclSubFolder )
                 for ( number j = 0; j < SubList.TagGroupCountTags(); j++ )
                 {
                         string file
                         if ( SubList.tagGroupGetIndexedTagAsString( j , file ) )
                                 fileList.TagGroupInsertTagAsString( Infinity() , file )
                 }
         }
 }
 return fileList

}

 

// Function removes entries not matching in suffix

TagGroup FilterFilesList( TagGroup list, string suffix )
{
 TagGroup outList = NewTagList()
 suffix = ToLowerCase( suffix )
 for ( number i = 0 ; i < list.TagGroupCountTags() ; i++ )
 {
         string origstr
         if ( list.TagGroupGetIndexedTagAsString( i , origstr ) ) 
         {
                 string str = ToLowerCase( origstr )
                 number matches = 1
                 if ( len( str ) >= len( suffix ) )                 // Ensure that the suffix isn't longer than the whole string
                 {
                         if ( suffix == right( str , len( suffix ) ) ) // Compare suffix to end of original string
                         {
                                 outList.TagGroupInsertTagAsString( outList.TagGroupCountTags() , origstr )        // Copy if matching
                         }
                 }
         }
 }
 return outList

}



////////////////////////////////////////////////////////////////////////////////////////

// Open and process all files in a fileList

void BatchProcessList( TagGroup fileList , string name )
{
 number nEntries = fileList.TagGroupCountTags()

 if ( nEntries > 0 )
         result( "Processing file list <" + name + "> with " + nEntries + " files.\n" )
 else
         result( "File list <" + name + "> does not contain any files.\n" )
 number blah
 for ( number i = 0 ; i < nEntries ; i++ )
 {
         string str 
         
         if ( fileList.TagGroupGetIndexedTagAsString( i , str ) )
			{image img := OpenImage( str )
                 if ( img.ImageIsValid() )
					{
					PerformBatchAction( img, str )
					HideImage(img)
					}//end image valid if
		}//end if file

	}//end for

}//end void
 
// Main routine. Processes all dm3/dm4 files in a directory into a file list and run process
void BatchProcessFilesInFolder( number includeSubFolders )
{
 string folder , outputFolder
 if ( !GetDirectoryDialog( "Select folder to batch process" , "" , folder ) ) 
         return
 
 TagGroup fileList = CreateFileList( folder, includeSubFolders ) 
 TagGroup fileListDM3 = FilterFilesList( fileList , ".dm3" )
 //BatchProcessList( fileListDM3 , "DM3 list" )
 TagGroup fileListDM4 = FilterFilesList( fileList , ".dm4" )
 Result("\n\n\n Processing folder "+folder)
 BatchProcessList( fileListDM4 , "DM4 list" )
}


 
BatchProcessFilesInFolder( 1 )
