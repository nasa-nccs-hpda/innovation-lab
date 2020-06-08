
import numpy as np

from celery import group

from model.CeleryConfiguration import app
from model.Chunker import Chunker

from projects.aviris_regression_algorithms.model.ApplyAlgorithm \
    import ApplyAlgorithm

# -----------------------------------------------------------------------------
# class ApplyAlgorithmCelery
# -----------------------------------------------------------------------------
class ApplyAlgorithmCelery(ApplyAlgorithm):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, csvFile, avirisImage, logger=None, numProcs=5):

        # Initialize the base class.
        super(ApplyAlgorithmCelery, self).__init__(csvFile, 
                                                   avirisImage, 
                                                   logger)
                                                   
        self._numProcs = numProcs
        
    # -------------------------------------------------------------------------
    # _processChunk
    # 
    # This is the distributed method.
    # -------------------------------------------------------------------------
    @staticmethod
    @app.task(serializer='pickle')
    def _processChunk(loc, xSize, ySize, imagePath, algorithmName,
                      normalizePixels, coefs):

        print ('In processChunk ...')
        
        # This chunker will actually read the pixels.
        chunker = Chunker(imagePath)
        chunker.setChunkSize(xSize, ySize)
        
        # This will only get a single chunk from the location specified.
        unusedLoc, chunk = chunker.getChunk(loc[0], loc[1])
        
        rows = np.split(chunk, chunk.shape[1], 1)
        chunkOut = {}
        chunkQa = {}
        rowNum = loc[1]
        
        for row in rows:

            chunkOut[rowNum], chunkQaBytes = \
                ApplyAlgorithm._processRow(row, algorithmName, normalizePixels,
                                           coefs)

            chunkQa[rowNum] = chunkQaBytes.decode('utf8')
            print('chunkOut size = ', len(chunkOut[rowNum]))
            rowNum += 1
            
        testReturn = np.zeros(50).tolist()
        return testReturn, None #chunkOut, chunkQa
        
    # -------------------------------------------------------------------------
    # processRaster
    # -------------------------------------------------------------------------
    def _processRaster(self, outDs, qa, algorithmName, normalizePixels):
        
        # ---
        # Set up a chunker to move through the image by several rows per chunk.
        # Each set of rows is sent to a process via Celery.
        # ---
        chunker = Chunker(self._imagePath)
        # xSize = chunker._imageFile._getDataset().RasterXSize
        xSize = int(chunker._imageFile._getDataset().RasterXSize / 4)
        
        # ySize = int(chunker._imageFile._getDataset().RasterYSize /
        #             self._numProcs)

        ySize = chunker._imageFile._getDataset().RasterYSize

        chunker.setChunkSize(xSize, ySize)

        # Collect all the chunk locations.
        locs = []
        
        while True:
            
            # ---
            # Set chunker to not read the pixels, only to return the chunk
            # location.  The chunks will be read from the distributed process.
            # ---
            loc, chunk = chunker.getChunk(None, None, False)

            if chunker.isComplete():
                break
                
            locs.append(loc)
            
        # Distribute the chunks.
        # locs = [locs[0]]        # ***** REMOVE THIS LINE AFTER TEST *****
        wpi = group(ApplyAlgorithmCelery._processChunk.s(
                                loc,
                                xSize,
                                ySize,
                                self._imagePath,
                                algorithmName,
                                normalizePixels,
                                self.coefs) for loc in locs)

        asyncResults = wpi.apply_async() # This initiates the processes.
        asyncResults.get()    # Waits for wpi to finish. 

        # # ar0[0].values()
        # # ar0[0].popitem()
        # # workers with connection errors:  10, then ok
        # for asyncResult in asyncResults.results:
        #
        #     chunkOut, chunkQa = asyncResult.get()
        #
        #     # Add to the output image.
        #     for key in chunkOut.keys():
        #
        #         chunk = chunkOut[key]
        #         rowNum = int(chunk[0])
        #         row = chunk[1]
        #
        #         # Refactor this.
        #         hexArray = b''
        #         for num in outArray:
        #             hexArray += struct.pack('f', num)
        #
        #         outDs.WriteRaster(0, curRow, xSize, 1, hexArray)
        #
        #     # Add to the QA image.
