from MindwaveDataPoints import RawDataPoint, PoorSignalLevelDataPoint,\
    AttentionDataPoint, MeditationDataPoint, BlinkDataPoint, EEGPowersDataPoint, BA_DataPoint,\
    UnknownDataPoint

EXTENDED_CODE_BYTE = 0x55

class MindwavePacketPayloadParser:
    
    def __init__(self, payloadBytes):
        self._payloadBytes = payloadBytes
        self._payloadIndex = 0
        #print ('Payload Bytes = ', self._payloadBytes)
        
    def parseDataPoints(self):
        dataPoints = []
        while (not self._atEndOfPayloadBytes()):
            dataPoint = self._parseOneDataPoint()
            dataPoints.append(dataPoint)
        return dataPoints
        
    def _atEndOfPayloadBytes(self):
        return self._payloadIndex == len(self._payloadBytes)
    
    def _parseOneDataPoint(self):
        dataRowCode = self._extractDataRowCode();
        dataRowValueBytes = self._extractDataRowValueBytes(dataRowCode)
        return self._createDataPoint(dataRowCode, dataRowValueBytes)
    
    def _extractDataRowCode(self):
        return self._ignoreExtendedCodeBytesAndGetRowCode()
        
    def _ignoreExtendedCodeBytesAndGetRowCode(self):
        # EXTENDED_CODE_BYTES seem not to be used according to 
        # http://wearcam.org/ece516/mindset_communications_protocol.pdf
        # (August 2012)
        # so we ignore them
        byte = self._getNextByte()
        while (byte == EXTENDED_CODE_BYTE):
            byte = self._getNextByte()
        dataRowCode = byte
        #print ('DRC= ', dataRowCode)
        return dataRowCode
       
    def _getNextByte(self):
        nextByte = self._payloadBytes[self._payloadIndex]
        #print ('Next Byte= ', nextByte)
        self._payloadIndex += 1
        return nextByte
    
    def _getNextBytes(self, amountOfBytes):
        #print ('Payload Index = ', self._payloadIndex)
        #print ('Payload Bytes = ', self._payloadBytes)
        nextBytes = self._payloadBytes[self._payloadIndex : self._payloadIndex + amountOfBytes]
        #print('nb = ', nextBytes)
        self._payloadIndex += amountOfBytes
        #print ('Payload Index = ', self._payloadIndex)
        return nextBytes
    
    def _extractDataRowValueBytes(self, dataRowCode):
        lengthOfValueBytes = self._extractLengthOfValueBytes(dataRowCode)
        dataRowValueBytes = self._getNextBytes(lengthOfValueBytes)
        #print('LVB = ', lengthOfValueBytes)
        #print('DRVBi = ', dataRowValueBytes)
        return dataRowValueBytes
    
    def _extractLengthOfValueBytes(self, dataRowCode):
        # If code is one of the mysterious initial code values
        # return before the extended code check
        if dataRowCode == 0xBA or dataRowCode == 0xBC:
            return 1

        dataRowHasLengthByte = dataRowCode > 0x7f
        if (dataRowHasLengthByte):
            return self._getNextByte()
        else:
            return 1
    '''   
    def _extractLengthOfValueBytes(self, dataRowCode):
        dataRowHasLengthByte = dataRowCode > 0x7f and dataRowCode < 0x85
        #print('LENGTH BYTE = ', dataRowHasLengthByte)
        if (dataRowHasLengthByte):
            return self._getNextByte()
        else:
            return 1
    '''    
    def _createDataPoint(self, dataRowCode, dataRowValueBytes):
        #print ('DRC= ', dataRowCode)
        #print ('DRVB= ', dataRowValueBytes)
        if (dataRowCode == 0x02):
            return PoorSignalLevelDataPoint(dataRowValueBytes)
        elif (dataRowCode == 0x04):
            return AttentionDataPoint(dataRowValueBytes)
        elif (dataRowCode == 0x05):
            return MeditationDataPoint(dataRowValueBytes)
        elif (dataRowCode == 0x16):
            return BlinkDataPoint(dataRowValueBytes)
        elif (dataRowCode == 0x80):
            return RawDataPoint(dataRowValueBytes)
        elif (dataRowCode == 0x83):
            return EEGPowersDataPoint(dataRowValueBytes)
        elif (dataRowCode == 0xBA):
            return UnknownDataPoint(dataRowValueBytes)
        elif (dataRowCode == 0xBC):
            return UnknownDataPoint(dataRowValueBytes)
        else:
            assert False 
        
        