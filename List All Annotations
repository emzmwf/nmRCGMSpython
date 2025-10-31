## Script to export annotations from GMS
## v 0.2 - get image name 
## MWF October 2025 for UoN


def AnnotationOutput(img_disp, name):
    print("\n ===== "+name)
    nSubComp = img_disp.CountChildren()
    for index in range(nSubComp):
        comp = img_disp.GetChild(index)
        if ( comp.GetType() == 13 ):
            print(comp.TextAnnotationGetText())
 

def RunOne():
    # if only running on front image
    testImg = DM.GetFrontImage()
    img_disp = testImg.GetImageDisplay(0)
    name = testImg.GetName()
    AnnotationOutput(img_disp, name)
    # Cleanup 
    del img_disp
    del testImg

def RunAll():
    # if running on all images in workspace
    # THIS BIT NOT WORKING YET
    ImageDocFront = DM.GetFrontImageDocument()
    wsID = ImageDocFront.GetWorkspace()
    nDoc = DM.CountImageDocuments()
    if ( 0 == nDoc ):
        exit( 0 )
    print("Identified "+str(nDoc)+" documents")
    for i in range(0,nDoc):
        try:
            #doc = DM.GetImageDocumentByID(i)
            doc = DM.GetImageDocument(i)
            if (doc == None):
                pass
        except:
            pass
        else:
            if doc is not None:
                testImg = doc.GetImage(0)
                name = testImg.GetName()
                img_disp = testImg.GetImageDisplay(0)
                AnnotationOutput(img_disp, name)
                del img_disp
                del testImg

print("\n \n \n \n")
bVal = DM.OkCancelDialog( 'OK for all images on workspace, or cancel for front only' )
if bVal == 0:
    RunOne()
if bVal == 1:
    RunAll()
