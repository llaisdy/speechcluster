#! /usr/bin/env python3

"""
* speechCluster: central API for SpeechCluster objects
"""

import audioop, math, os, re, wave

from .utils import file_write

silence = b'\x00\x00' * 8000 # half a second's silence

class SpeechCluster:
    formatDict = {'.seg': 'esps',
                  '.lab': 'esps',
                  '.htk-lab': 'htk-lab',
                  '.htk-grm': 'htk-grm',
                  '.esps': 'esps',
                  '.textgrid': 'TextGrid',
                  '.textGrid': 'TextGrid',                  
                  '.transcription': 'transcription', # SphinxTrain
                  '.wav': 'wav',
                  '.pm': 'pitchmark'}
    sepDict = {'esps': ' ',
               'htk-lab': ' ',
               'TextGrid': '='}
    endHeadDict = {'esps': '#',
                   'htk-lab': '\n',
                   'TextGrid': '\n'}
    timesDict = {'ms': .001, 'sec': 1, 'min': 60}

    def __init__(self, segFn='', debug=False):
        self.debug = debug

        self.audioFn = ''
        self.audioData = None # string of bytes for wav files
        self.audioFormat = ''
        self.audioSampleRate = 0
        self.audioSampleSize = 0 # in bytes

        self.segFn = segFn
        self.fstem = ''
        self.segFormat = ''
        self.dataMin = 0
        self.dataMax = 0

        self.head = {} # misc metadata read from the file header
        self.tiers = []
        self.mergeDict = {}

        if segFn: self.read_format(segFn)

    def getHeadBody(self, fn, sep):
        with open(fn) as f:
            data = list(f)
            # lines with misc whitespace --> '\n'
            # TODO: or with misc whitespace at end of line
            for i in range(len(data)):
                m = re.match(r'\s+', data[i])
                if m and m.end() == len(data[i]):
                    data[i] = '\n'
            hidx = data.index(sep) + 1
            head, body = data[0:hidx], data[hidx:]
            return head, body

    def updateTiers(self, tier):
        tier.dataMax = max(self.dataMax, tier[-1].max)
        self.tiers.append(tier)
        maxes = [t.dataMax for t in self.tiers]
        self.dataMax = max(maxes)
        for t in self.tiers:
            t.dataMax = self.dataMax

    def getTierByName(self, tierName):
        for t in self.tiers:
            if t.getName() == tierName:
                return t

    def replaceLabs(self, replaceDict):
        keys = replaceDict.keys()
        spacedKeys = {}
        for k in [k for k in keys if ' ' in k]:
            spacedKeys[k.split()[0]] = (k, replaceDict[k])
        spk = spacedKeys.keys()
        insertions = []
        for i in range(len(self.tiers)):
            j = 0
            newLab = '!!merge'
            while j < len(self.tiers[i]):
                lab = self.tiers[i][j].label
                if lab in keys:
                    newLab = replaceDict[lab]
                    if newLab == '!!merge':
                        self.removeSegnFromTiern(j, i)
                    else:
                        self.tiers[i][j].label = newLab
                        j += 1
                elif spacedKeys and (lab in spk):
                    # eg /t sh/ -> /ch/
                    secondOldLabel = spacedKeys[lab][0].split()[1]
                    newLabel = spacedKeys[lab][1]
                    if self.debug is True:
                        print('%s + %s -> %s' \
                              % (lab, secondOldLabel, newLabel))
                    if self.tiers[i][j+1].label == secondOldLabel:
                        newseg = Segment()
                        newseg.min = self.tiers[i][j].min
                        newseg.max = self.tiers[i][j+1].max
                        newseg.label = newLabel
                        insertions.append((newseg, i))
                        self.tiers[i][:] = self.tiers[i][:j] \
                                           + self.tiers[i][j+2:]
                    j += 1
                else: j += 1
        for seg, i in insertions:
            self.tiers[i].insertSegment(seg)

    def removeSegnFromTiern(self, segn, tiern):
        oldSegs = self.tiers[tiern]
        self.tiers[tiern][segn-1].max = oldSegs[segn].max
        self.tiers[tiern][:] = oldSegs[:segn] + oldSegs[segn+1:]
        
    def read_ESPS(self, fn):
        """
        Returns ["head", [time, something_else, label]]
        """
        try:
            head, body = self.getHeadBody(fn, '#\n')
        except: # probably htk-lab
            self.read_HTKLab(fn)
        else:
            self.parseHead(head, 'esps')
            tier = SegmentationTier()
            tier.setName('Phone') # TODO: magic text!
            if body:
                for line in body:
                    fields = line.split()
                    # fields[0] = time
                    # fields[1] = something_else  - TODO: Q: what is it?
                    # fields[2] = label
                    if len(fields) != 3:
                        if self.debug is True:
                            print('DEBUG: N FIELDS: %s line: %s' % (fn, line))
                            print(tier)
                        #else:
                        pass # what then!?
                    else:
                        seg = Segment()
                        if tier:
                            seg.min = tier[-1].max
                        else: seg.min = 0
                        seg.max = eval(fields[0])
                        seg.label = fields[-1]
                        tier.append(seg)
                self.updateTiers(tier)

    def read_HTKLab(self, fn):
        """
        Returns ["head", [start time, end time, label]]
        """
        body = list(open(fn))

        # sometimes there is no header
        if len(body[0].strip().split()) == 1:
            head = body.pop(0)
        else: head = ''
        
        tier = SegmentationTier()
        tier.setName('Phone') # TODO: magic text!
        if body:
            for line in body:
                fields = line.split()
                # fields[0] = start time
                # fields[1] = end time
                # fields[2] = label
                if len(fields) != 3:
                    if self.debug is True:
                        print('DEBUG: N FIELDS: %s line: %s' % (fn, line))
                        print(tier)
                    #else:
                    pass # what then!?
                else:
                    seg = Segment()
                    seg.min = eval(fields[0])/10000000.0
                    seg.max = eval(fields[1])/10000000.0
                    seg.label = fields[-1]
                    tier.append(seg)
            self.updateTiers(tier)

    def read_TextGrid(self, fn):
        # TODO: doesn't read in pitch tier!
        head, body = self.getHeadBody(fn, '\n')
        self.parseHead(head, 'TextGrid')
        # the following non-indented lines can be skipped
        while body[0][0] not in [' ', '\t']: body.pop(0)
        # there follows a list of 'item [n]:'
        itemList = ''.join(body).split('item')[1:]
        for item in itemList:
            il = item.split('\n')
            #if il[1].strip() == 'class = "TextTier"':
            #    # TODO: skips pitch tiers!
            #    continue
            # if sc works withthis commented out,
            # delete it
            content = [l.strip() for l in il[1:]]
            tier = SegmentationTier()
            # first 2 lines should be class then name
            tier.head['class'] = re.search('class = "(.*?)"',
                                           content[0]).group(1)
            tier.head['name'] = re.search('name = "(.*?)"',
                                           content[1]).group(1)
            #skip till we get to the intervals
            while content and ( len(content[0]) < 12 or \
                                content[0][:10] != 'intervals ' ):
                content.pop(0)
            # each interval is 4 lines: head, xmin, xmax, text
            while content:
                interval = content[0:4]
                if len(interval) == 4:
                    seg = Segment()
                    seg.label = re.search('text = "(.*?)"',
                                          interval[3]).group(1)
                    seg.min = eval(interval[1].split('=')[1].strip())   #xmin
                    seg.max = eval(interval[2].split('=')[1].strip())   #xmax
                    tier.append(seg)
                    content = content[4:]
                else: content = []
            if len(tier):
                self.updateTiers(tier)

    def read_pm(self, fn): #### TODO
        #Hacky version quickly
        data = list(open(fn))[8:] # discard header
        tier = SegmentationTier()
        tier.setName('Pitch')
        tier.head['class'] = 'TextTier'
        for t in [line.split()[0] for line in data]:
            seg = Segment()
            seg.min = seg.max = eval(t)
            tier.append(seg)
        self.updateTiers(tier)
    
    def parseHead(self, head, format='esps'):
        """
        if header is name = value format: make dict
        else: dict keys are line nos
        """
        sep = self.sepDict[format]
        endh = self.endHeadDict[format]
        for i in range(len(head)):
            line = head[i]
            if sep in line:
                name = line.split(sep)[0]
                value = ' '.join(line.split(sep)[1:])
                self.head.setdefault(name.strip(), []).append(value.strip())
            elif line[:-1] == endh:
                return
            else: pass # what else could happen?

    def merge(self, other):
        self.mergeDict[other.segFn] = other.head
        for tier in other.tiers:
            self.updateTiers(tier)
        if other.audioData:
            self.audioFn = other.audioFn
            self.audioData = other.audioData
            self.audioFormat = other.audioFormat
            self.audioSampleRate = other.audioSampleRate
            self.audioSampleSize = other.audioSampleSize
            

    def write_ESPS(self, format, tierName='Phone'):
        ### TODO magic text! only one tier!
        out = '%s\n' % (self.writeHead(format))
        # TODO what about writing multiple tiers?
        if len(self.tiers) > 1:
            tier = self.getTierByName(tierName)
        else:
            tier = self.tiers[0]
        for segment in tier:
            out = '%s\t%s\t125 %s\n' \
                  % (out, segment.max, segment.label)
        # todo: tier separator in esps format!?
        return out

    def write_HTKLab(self, tierName='Phone'):
        ### TODO: magic text! only one tier!
        out = '%s.lab\n' % self.fstem
        if len(self.tiers) > 1:
            tier = self.getTierByName(tierName)
        else:
            tier = self.tiers[0]
        for segment in tier:
            out = '%s%s %s %s\n' \
                  % (out,
                     int(segment.min*10000000),
                     int(segment.max*10000000), segment.label)
        # todo: tier separator in esps format!?
        out = '%s.\n' % out
        return out

    def write_HTKGrm(self, tier='Word'):
        """HTK gram*.txt format
        $sentence = lab1 lab2 lab3 ... labn;
        ($sentence)
        """
        if len(self.tiers) > 1:
            tier = self.getTierByName(tier)
        else:
            tier = self.tiers[0]
        labList = [seg.label for seg in tier]
        labels = ' '.join(labList)
        out = '$utterance = %s;\n($utterance)\n' % (labels)
        return out

    def write_stt(self):
        # TODO: for now assume a single phone tier
        labList = [seg.label for seg in self.tiers[0]]
        if labList[0] == 'sil': labList = labList[1:]
        if labList[-1] == 'sil': labList = labList[:-1]
        labels = ' '.join(labList).replace('sil', '<sil>')
        out = '<s> %s </s> (%s)' % (labels, self.fstem)
        return out
    
    def write_TextGrid(self):
        out = '%s\n' % (self.writeHead('tg'))
        out = '%sxmin = %s\n' % (out, self.dataMin)
        out = '%sxmax = %s\n' % (out, self.dataMax)
        out = '%stiers? <exists>\n' % out # assume tiers exist
        out = '%ssize = %d\n' % (out, len(self.tiers))
        out = '%sitem []: \n' % out
        for i in range(len(self.tiers)):
            tier = self.tiers[i]
            out = '%s\titem [%d]:\n' % (out, i+1)
            tierClass = tier.head.get('class', 'IntervalTier')
            out = '%s\t\tclass = "%s"\n' \
                  % (out, tierClass)
            out = '%s\t\tname = "%s"\n' \
                  % (out, tier.head.get('name', 'Labels'))
            out = '%s\t\txmin = %s\n' % (out, tier.dataMin)
            out = '%s\t\txmax = %s\n' % (out, tier.dataMax)
            if tierClass == 'IntervalTier':
                out = '%s\t\tintervals: size = %d\n' % (out, len(tier))
                for i in range(len(tier)):
                    seg = tier[i]
                    out = '%s\t\tintervals [%d]:\n\t\t\txmin = %s\n\t\t\txmax = %s\n\t\t\ttext = "%s"\n' \
                          % (out, i+1, seg.min, seg.max, seg.label)

            elif tierClass == 'TextTier':
                out = '%s\t\tpoints: size = %d\n' % (out, len(tier))
                for i in range(len(tier)):
                    seg = tier[i]
                    out = '%s\t\tpoints [%d]:\n\t\t\ttime = %s\n\t\t\tmark = "%s"\n' \
                          % (out, i+1, seg.max, seg.label)
                
        return out

    def writeHead(self, format='esps'):
        out = ''
        if format == 'esps':
            order = ['signal', 'type', 'comment',
                     'separator', 'nfields']
            otherkeys = [i for i in self.head.keys() if i not in order]
            for key in order:
                for i in self.head.get(key, ['UNDEF']):
                    out = '%s%s %s\n' % (out, key, i)
            for key in otherkeys:
                for i in self.head[key]:
                    out = '%s%s %s\n' % (out, key, i)
            out = '%s#\n' % out
        elif format == 'lab':
            # hack for festival format lab files
            out = 'separator ;\nnfields 1\n#'
        elif format == 'tg':
            out = 'File type = "ooTextFile"\nObject class = "TextGrid"\n'
            # TODO: add other (nonTextGrid) header items as comments
            # TODO: Q: What is TextGrid comment marker?
        return out

    def getStartEnd(self, windowSize=0.25):
        noiseTimes = []
        data = wave.open(self.audioFn)
        width = data.getsampwidth()
        frate = data.getframerate()
        nframes = data.getnframes()
        endTime = nframes*1.0/frate
        rmsFull = audioop.rms(data.readframes(nframes), width)
        #print('rmsFull = ', rmsFull)
        data.rewind()
        window = int(frate*windowSize)
        step = int(window/2)
        while data.tell() < nframes-step:
            sample = data.readframes(window)
            rms = audioop.rms(sample, width)
            if rms > rmsFull/10:
                now = data.tell()*1.0/frate
                noiseTimes.append(now)
                #print('%s\t%s' % (rms, now))
            #else:
            #    print(rms)
            data.setpos(data.tell()-step)
        return noiseTimes[0]-(windowSize/2), noiseTimes[-1], endTime

    def setStartEnd(self, newStart, newEnd):
        start_b = int(newStart * self.audioSampleRate
                      * self.audioSampleSize)
        # the following checks start point is at a sample start point
        if math.modf(start_b/(self.audioSampleSize*1.0))[0] != 0.0:
            start_b += 1
        stop_b = int(newEnd * self.audioSampleRate
                     * self.audioSampleSize)
        # pad either end with artificial silence
        self.audioData = self.audioData[start_b:stop_b]
        # change label tiers
        self.dataMax = newEnd - newStart
        for i in range(len(self.tiers)):
            for j in range(len(self.tiers[i])):
                if j != 0:
                    self.tiers[i][j].min = self.tiers[i][j].min - newStart
                self.tiers[i][j].max = self.tiers[i][j].max - newStart


    def read_wav(self, fn):
        data = wave.open(fn)
        nframes = data.getnframes()
        self.audioData = data.readframes(nframes)
        self.audioFormat = 'wav'
        self.audioSampleRate = data.getframerate()
        self.audioSampleSize = data.getsampwidth()
        self.audioFn = fn

    def write_wav(self, fn='', start_t=0, stop_t=0):
        """
        t = secs
        """
        if not fn: fn = self.audioFn
        out = wave.open(fn, 'wb')
        out.setnchannels(1) # assume mono
        out.setframerate(self.audioSampleRate)
        out.setsampwidth(self.audioSampleSize)
        if not (start_t or stop_t): audioData = self.audioData
        else:
            start_b = int(start_t * self.audioSampleRate
                          * self.audioSampleSize)
            # the following checks start point is at a sample start point
            if math.modf(start_b/(self.audioSampleSize*1.0))[0] != 0.0:
                start_b += 1
            stop_b = int(stop_t * self.audioSampleRate
                          * self.audioSampleSize)
            # pad either end with artificial silence
            audioData = self.audioData[start_b:stop_b]
            if start_b != 0:
                audioData = silence + audioData
            audioData += silence
        out.writeframes(audioData)
        out.close()

    def read_format(self, fn):
        import os
        fstem, fext = os.path.splitext((os.path.basename(fn)))
        if fext:
            self.fstem = fstem
            format = self.formatDict.get(fext.lower(), None)
            if format == 'esps': self.read_ESPS(fn)
            elif format == 'TextGrid': self.read_TextGrid(fn)
            elif format == 'wav': self.read_wav(fn)
            elif format == 'htk-lab': self.read_HTKLab(fn)
            elif format == 'pitchmark': self.read_pm(fn)
            else: pass # unsupported format, ignore
            self.segFormat = format
        else: # fn is a stem; load all files with same stem (inc audio)
            path, fn = os.path.split(fn)
            self.fstem = fn
            if path:
                fnList = ['%s%s%s' % (path, os.path.sep, fn)
                          for fn in os.listdir(path)
                          if os.path.splitext(fn)[0] == fstem]
            else:
                fnList = [fn for fn in os.listdir(os.getcwd())
                          if os.path.splitext(fn)[0] == fstem]
            for fn in fnList:
                seg = SpeechCluster(fn)
                self.merge(seg)

    def write_format(self, format=''):
        if not format:
            format = self.segFormat
        if format == 'esps' or format == 'lab':
            out = self.write_ESPS(format)
        elif format == 'TextGrid':
            out = self.write_TextGrid()
        elif format == 'transcription':
            out = self.write_stt()
        elif format in ['htk', 'htk-lab']:
            out = self.write_HTKLab()
        elif format == 'htk-grm':
            out = self.write_HTKGrm()
        return out

    def split(self, splitCriteria, saveDir='', saveSegFormat='esps'):
        """splitCriteria new format:
        {'n' = <integer>,
         'tier' = <tierName>,
         'label' = <label, optional>,
         'step' = <integer, optional>}
        """
        if not saveDir:
            # saveDir = '%s.d' % self.fstem or similar
            pass
        # if not os.path.exists(saveDir): mkdir(saveDir)
        if not splitCriteria.get('label'):
            if splitCriteria['tier'] in self.timesDict:
                self.splitByTime(splitCriteria['n'],
                                 splitCriteria['tier'],
                                 splitCriteria.get('step', 1),
                                 saveDir, saveSegFormat)
            else:
                # split by each n intervals in tier
                self.splitByTier(splitCriteria['n'],
                                 splitCriteria['tier'],
                                 splitCriteria.get('step', 1),
                                 saveDir, saveSegFormat)
        else:
            # split by each n occurrences of label
            self.splitByLabel(splitCriteria['n'],
                              splitCriteria['tier'],
                              splitCriteria['label'],
                              saveDir, saveSegFormat)

    def splitByTime(self, n, timeName, step, saveDir, saveSegFormat):
        import copy
        count = 1
        dataMin = 0
        window = self.parseTime(n, timeName)
        step = self.parseTime(step, timeName)
        dataMax = window
        while dataMin < self.dataMax:
            # split seg tiers
            newSeg = SpeechCluster()
            for tier in self.tiers:
                newTier = tier.getSlice(dataMin, dataMax)
                # pad for silence
                if dataMin == 0: pad = 0
                else: pad = 0.5 - dataMin
                for seg in newTier:
                    seg.min += pad
                    seg.max += pad
                # final silence pad
                silSeg = Segment()
                silSeg.label = 'sil'  # TODO: magic text!
                silSeg.min = newTier[-1].max
                silSeg.max = silSeg.min + 0.5
                newTier.append(silSeg)
                if pad:
                    # initial silence pad
                    silSeg = Segment()
                    silSeg.label = 'sil'
                    silSeg.min = 0
                    silSeg.max = 0.5
                    newTier.insert(0, silSeg)
                newSeg.updateTiers(newTier)
            # save seg file
            newSeg.fstem = '%s_%03d' % (self.fstem, count)
            saveFn = '%s%s%s.%s' \
                     % (saveDir, os.path.sep,
                        newSeg.fstem, saveSegFormat)
            file_write(saveFn, newSeg.write_format(saveSegFormat))
            # split and save wav
            saveWavFn = '%s%s%s_%03d.wav' \
                        % (saveDir, os.path.sep, self.fstem, count)
            self.write_wav(saveWavFn, dataMin, dataMax)
            # update
            count += 1
            dataMin += step
            dataMax += window

    def parseTime(self, n, timeName):
        """returns no. of seconds"""
        return n * self.timesDict[timeName]

    def splitByTier(self, n, tierName, step, saveDir, saveSegFormat):
        # TODO: for now assume wav format audio
        import copy # see below for reason
        tier = self.getTierByName(tierName)
        count = 1
        while tier:
            theseSegs = copy.deepcopy(tier[:n])
            tier = tier[step:]
            # split and save seg tier
            newSeg = SpeechCluster()
            newTier = SegmentationTier()
            newTier.setName(tierName)
            dataMin = theseSegs[0].min
            dataMax = theseSegs[-1].max
            # pad for silence
            if dataMin == 0: pad = 0
            else: pad = 0.5 - dataMin
            for seg in theseSegs:
                seg.min = seg.min + pad
                seg.max = seg.max + pad
                newTier.append(seg)
            # final silence pad
            silSeg = Segment()
            silSeg.label = 'sil'
            silSeg.min = newTier[-1].max
            silSeg.max = silSeg.min + 0.5
            newTier.append(silSeg)
            if pad:
                # initial silence pad
                silSeg = Segment()
                silSeg.label = 'sil'
                silSeg.min = 0
                silSeg.max = 0.5
                newTier.insert(0, silSeg)
            newTier.setName(tierName)
            newSeg.updateTiers(newTier)
            newSeg.fstem = '%s_%03d' % (self.fstem, count)
            saveFn = '%s%s%s.%s' \
                     % (saveDir, os.path.sep, newSeg.fstem, saveSegFormat)
            file_write(saveFn, newSeg.write_format(saveSegFormat))
            # split and save wav
            saveWavFn = '%s%s%s_%03d.wav' \
                        % (saveDir, os.path.sep, self.fstem, count)
            self.write_wav(saveWavFn, dataMin, dataMax)
            # update
            count += 1

    def splitByLabel(self, n, tierName, label,
                     saveDir, saveSegFormat):
        # TODO: for now assume wav format audio
        import copy # see below for reason
        tier = self.getTierByName(tierName)
        count = 1
        while tier:
            if len(tier) >= 6:
                # TODO: magic no. 5 = min segs allowed
                theseSegs = copy.deepcopy(tier[:n])
                # nb: theseSegs=tier[:n] causes weird error
                tier = tier[1:] # TODO: magic no. 1 = window step
            else:
                theseSegs = tier
                tier = []
            # split and save seg tier
            newSeg = SpeechCluster()
            newTier = SegmentationTier()
            dataMin = theseSegs[0].min
            dataMax = theseSegs[-1].max
            # pad for silence
            if dataMin == 0: pad = 0
            else: pad = 0.5 - dataMin
            for seg in theseSegs:
                seg.min = seg.min + pad
                seg.max = seg.max + pad
                newTier.append(seg)
            # final silence pad
            silSeg = Segment()
            silSeg.label = 'sil'
            silSeg.min = newTier[-1].max
            silSeg.max = silSeg.min + 0.5
            newTier.append(silSeg)
            if pad:
                # initial silence pad
                silSeg = Segment()
                silSeg.label = 'sil'
                silSeg.min = 0
                silSeg.max = 0.5
                newTier.insert(0, silSeg)
            newTier.setName(tierName)
            newSeg.updateTiers(newTier)
            newSeg.fstem = '%s_%03d' % (self.fstem, count)
            saveFn = '%s%s%s.%s' \
                     % (saveDir, os.path.sep, newSeg.fstem, saveSegFormat)
            file_write(saveFn, newSeg.write_format(saveSegFormat))
            # split and save wav
            saveWavFn = '%s%s%s_%03d.wav' \
                        % (saveDir, os.path.sep, self.fstem, count)
            self.write_wav(saveWavFn, dataMin, dataMax)
            # update
            count += 1

##        ch_wave -scaleN 0.9 $i -F 16000 -o /tmp/tmp$$.wav
##        pitchmark /tmp/tmp$$.wav -o pm/$fname.pm \
##                  -otype est -min 0.005 -max 0.012 -fill -def 0.01 \
##                  -wave_end -lx_lf 200 -lx_lo 71 -lx_hf 80 -lx_ho 71 -med_o 0

    pitchCmd1 = 'ch_wave -scaleN 0.9 *WAV_FN* -F 16000 -o tmp.wav'

    pitchCmd2 = 'pitchmark tmp.wav -o *FSTEM*.pm ' \
                '-otype est -min *MIN* -max *MAX* -fill -def 0.01 ' \
                '-wave_end -lx_lf 200 -lx_lo 71 -lx_hf 80 -lx_ho 71 -med_o 0'

    pitchGenderDict = {'male': ('0.005', '0.012'),
                       'female': ('0.0033', '0.7')}

    def getPitchmarks(self, speakerGender='female'):
        if not self.getTierByName('Pitch'):
            cmd = self.pitchCmd1.replace('*WAV_FN*', self.audioFn)
            os.system(cmd)
            pgmin, pgmax = self.pitchGenderDict[speakerGender]
            cmd = self.pitchCmd2.replace('*MIN*', pgmin)
            cmd = cmd.replace('*MAX*', pgmax)
            cmd = cmd.replace('*FSTEM*', self.fstem)
            os.system(cmd)
            seg = SpeechCluster('%s.pm' % self.fstem)
            self.merge(seg)

    def getNearestOptimum(self, t):
        ## get nearest optimum cutpoint
        ## - upwards zero-crossing
        ## - just after a pitchmark
        
        # find nearest pitchmark before t
        tier = self.getTierByName('Pitch')
        marks = [seg.max for seg in tier if seg.max < t]
        if marks: mark = marks[-1]
        else: mark = t
            
        # get first upward zero-crossing after it
        # version 0.0.1: no smoothing or rolling averages
        w = wave.open(self.audioFn)
        f = int(mark * w.getframerate())
        w.setpos(f)
        val = self.frame2int(w.readframes(1))
        while  val > 0:
            val = self.frame2int(w.readframes(1))
        while val < 0:
            val = self.frame2int(w.readframes(1))
        f = w.tell()
        mark = f * 1.0 / w.getframerate()

        ## this would be better, but maybe too much fuss
        ## delta1
        ## find nearest pitchmark after t
        ## delta2 < delta1?
        ## get first zero-crossing after it
        ## delta3 < delta1?
        ## return best (zero-crossing with delta1 or 3)
        return mark

    def frame2int(self, frame):
        x = frame[0]
        y = frame[1]
        z = (y*256) + x
        if y > 127:
            z -= 65536
        return z


class SegmentationTier(list):
    def __init__(self):
        list.__init__(self)
        self.head = {} # name = value pairs eg in TextGrids
        #self.labelsetFn = '' # full path
        #self.labelset = None  # loaded labelset object [future]
        self.dataMin = 0
        self.dataMax = 0

    def getName(self):
        return self.head.get('name', 'unnamed')

    def setName(self, newName):
        self.head['name'] = newName

    def getSlice(self, min, max): #########DONE UP TO HERE
        if min < 0: min = 0
        if max > self.dataMax: max = self.dataMax
        newSlice = SegmentationTier()
        newSlice.setName(self.getName())
        for seg in self:
            if seg.max >= min and seg.min <= max:
                newSeg = Segment()
                newSeg.label = seg.label
                newSeg.min = seg.min #- min
                newSeg.max = seg.max #- min
                newSlice.append(newSeg)
        return newSlice

    def insertSegment(self, segment):
        self.append(segment)
        l = [(s.min, s.max, s) for s in self]
        l.sort()
        self[:] = [i[2] for i in l]

class Segment:
    def __init__(self):
        self.min = 0 # start time
        self.max = 0 # stop time
        self.label = '' # None; label object from labelset [future];
                        # for now: string

    def __str__(self):
        return '%s\t(%s, %s)' % (self.label, self.min, self.max)

    def __eq__(self, other):
        if isinstance(other, Segment):
            return self.label == other.label and \
                self.min == other.min and \
                self.max == other.max
        return NotImplemented

def printUsage():
    print("""
Label file converter.

""")
