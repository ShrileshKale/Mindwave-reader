import g_var   
import requests   
class DataPoint:
    def __init__(self, dataValueBytes):
        self._dataValueBytes = dataValueBytes


class UnknownDataPoint(DataPoint):
    def __init__(self, dataValueBytes):
        DataPoint.__init__(self, dataValueBytes)
        self.unknownPoint = self._dataValueBytes[0]

    def __str__(self):
        retMsgString = "Unknown OpCode. Value: {}".format(self.unknownPoint)
        return retMsgString
    
class PoorSignalLevelDataPoint(DataPoint):
    def __init__(self, dataValueBytes):
        DataPoint.__init__(self, dataValueBytes)
        self.amountOfNoise = self._dataValueBytes[0];
        g_var.PSL = (100 - self.amountOfNoise)

    def headSetHasContactToSkin(self):
        return self.amountOfNoise < 200;

    
    def __str__(self):
        poorSignalLevelString = "Poor Signal Level: " + str(self.amountOfNoise)
        #gvar.PSL = self.amountOfNoise + 100
        #poorSignalLevelString = ""
        if (not self.headSetHasContactToSkin()):
            poorSignalLevelString += " - NO CONTACT TO SKIN"
        return poorSignalLevelString
        

class AttentionDataPoint(DataPoint):
    def __init__(self, _dataValueBytes):
        DataPoint.__init__(self, _dataValueBytes)
        self.attentionValue = self._dataValueBytes[0]
        g_var.attentation_val = self.attentionValue

    
    def __str__(self):
#        return "Attention Level: " + str(self.attentionValue)
        #return ""
	data_logs = {
			"attention_level": self.attentionValue
	       	}
        response = requests.post('http://192.168.1.104:8000/data' ,json=data_logs)
	print response
	return "Attention Level:" + str(self.attentionValue)
        

class MeditationDataPoint(DataPoint):
    def __init__(self, _dataValueBytes):
        DataPoint.__init__(self, _dataValueBytes)
        self.meditationValue = self._dataValueBytes[0]
        g_var.meditation_val = self.meditationValue

    def __str__(self):
        return "Meditation Level: " + str(self.meditationValue)
        #return ""

class BlinkDataPoint(DataPoint):
    def __init__(self, _dataValueBytes):
        DataPoint.__init__(self, _dataValueBytes)
        self.blinkValue = self._dataValueBytes[0]

    def __str__(self):
        return "Blink Level: " + str(self.blinkValue)
    

class BA_DataPoint(DataPoint):
    def __init__(self, _dataValueBytes):
        DataPoint.__init__(self, _dataValueBytes)
        self.BAValue = self._dataValueBytes[0]

    def __str__(self):
        return "BS Data: " + str(self.attentionValue)
	#data_logs = {
         #          "attention_level": self.attentionValue
	#	}
       	#response = request.post(http://127.0.0.1:8000/data, json=data_logs)

class RawDataPoint(DataPoint):
    def __init__(self, dataValueBytes):
        DataPoint.__init__(self, dataValueBytes)
        self.rawValue = self._readRawValue()

    def _readRawValue(self):
        firstByte = self._dataValueBytes[0]
        secondByte = self._dataValueBytes[1]
        # TODO(check if this is correct iwth soem more tests..
        # and see http://stackoverflow.com/questions/5994307/bitwise-operations-in-python
        rawValue = firstByte * 256 + secondByte;
        if rawValue >= 32768:
            rawValue -= 65536
        return rawValue # hope this is correct ;)

    def __str__(self):
        return "Raw Value: " + str(self.rawValue)

class EEGPowersDataPoint(DataPoint):
    def __init__(self, dataValueBytes):
        DataPoint.__init__(self, dataValueBytes)
        self._rememberEEGValues();
        
    def _rememberEEGValues(self):
        self.delta = self._convertToBigEndianInteger(self._dataValueBytes[0:3]);
        self.theta = self._convertToBigEndianInteger(self._dataValueBytes[3:6]);
        self.lowAlpha = self._convertToBigEndianInteger(self._dataValueBytes[6:9]);
        self.highAlpha = self._convertToBigEndianInteger(self._dataValueBytes[9:12]);
        self.lowBeta = self._convertToBigEndianInteger(self._dataValueBytes[12:15]);
        self.highBeta = self._convertToBigEndianInteger(self._dataValueBytes[15:18]);
        self.lowGamma = self._convertToBigEndianInteger(self._dataValueBytes[18:21]);
        self.midGamma = self._convertToBigEndianInteger(self._dataValueBytes[21:24]);
        
        
        g_var.delta_val = self.delta
        g_var.theta_val = self.theta
        g_var.lowAlpha_val = self.lowAlpha
        g_var.highAlpha_val = self.highAlpha
        g_var.lowBeta_val = self.lowBeta
        g_var.highBeta_val = self.highBeta
        g_var.lowGamma_val = self.lowGamma
        g_var.midGamma_val = self.midGamma
    
        
        
    def _convertToBigEndianInteger(self, threeBytes):
        # TODO(check if this is correct iwth soem more tests..
        # and see http://stackoverflow.com/questions/5994307/bitwise-operations-in-python
        # only use first 16 bits of second number, not rest inc ase number is negative, otherwise
        # python would take all 1s before this bit...
        # same with first number, only take first 8 bits...
        bigEndianInteger = (threeBytes[0] << 16) |\
         (((1 << 16) - 1) & (threeBytes[1] << 8)) |\
          ((1 << 8) - 1) & threeBytes[2]
        return bigEndianInteger
        
    def __str__(self):
        return """EEG Powers:
                delta: {self.delta}
                theta: {self.theta}
                lowAlpha: {self.lowAlpha}
                highAlpha: {self.highAlpha}
                lowBeta: {self.lowBeta}
                highBeta: {self.highBeta}
                lowGamma: {self.lowGamma}
                midGamma: {self.midGamma}
                """.format(self = self)
        return """ """.format(self = self)
