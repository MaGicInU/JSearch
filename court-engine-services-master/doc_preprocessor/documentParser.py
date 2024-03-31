import datetime
import re
import datefinder


class DocumentParser():

    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.textSections = []
        self.sections = []
        self.text = re.sub(r'[^\x00-\x7F]+', " ", raw_text)
        self.text = self.text.replace("\xc2\xa0", " ").lower()
        self.lines = self.text.split("\n")
        self.petitioner_list = []
        self.respondent_list = []
        self.judgementDate_list = []
        self.courtType = ""
        self.state = ""
        self.judgementNumber = 0

    def parse(self):
        # Petitioner
        self.petitioner_list.extend(self.extractParam(
            "petitioner", ["vs", "versus", "respondent"], 5))
        self.petitioner_list.extend(self.extract_before_keyword("appellant"))
        self.petitioner_list.extend(self.extract_before_keyword("petitioner"))

        # Respondent
        self.respondent_list.extend(self.extract_before_keyword("respondent"))
        self.respondent_list.extend(self.extractParam(
            "respondent", ["judgment", "bench"], 5))

        # Petitioner & Respondent Merged
        res = self.getPetitionerAndRespondent()
        self.petitioner_list.append(res[0])
        self.respondent_list.append(res[1])

        # JudgementDate
        self.judgementDate_list.extend(
            self.extractDateParam("date of judgment"))
        self.judgementDate_list.extend(self.extractAllDates())

        # sections
        self.parseSections()

        # Court type
        self.setCourtType()

        # Judgement Number
        self.setJudgementNumber()
        return {
            "petitioner": self.petitioner_list,
            "respondent": self.respondent_list,
            "date": self.judgementDate_list,
            "section": self.sections,
            "text_sections": self.textSections,
            "court": self.courtType,
            "JudgementNumber": self.judgementNumber,
            "highCourtLocation": self.state,
            "queryText": self.text
        }

    def parseSections(self):
        self.parseSectionsCivil()
        self.parseSectionsCriminal()

    def setCourtType(self):
        lines = self.lines
        for line in lines:
            if("high court" in line.lower()):
                self.courtType = "High Court"
                self.setState(line)
                return
            elif("supreme court" in line.lower()):
                self.courtType = "Supreme Court"
                return
            else:
                self.courtType = "Unknown"

    def setJudgementNumber(self):
        lines = self.lines
        for line in lines:
            judgementNumberLine = ""
            if(" no." in line.lower()):
                judgementNumberLine = line.lower().split(" no.")[1].strip()
                self.judgementNumber = judgementNumberLine
                return
            elif(" no(s)." in line.lower()):
                judgementNumberLine = line.lower().split(" no(s).")[1].strip()
                self.judgementNumber = judgementNumberLine
                return

    def setState(self, line: str):
        if(" at " in line.lower()):
            self.state = line.lower().split(" at ")[1].strip()
        elif(" of " in line.lower()):
            self.state = line.lower().split(" of ")[1].strip()

    def parseSectionsCivil(self):
        singleLineText = self.text.replace("\n", " ")
        sections = re.findall(
            "section\s[\w\s]*act,*[\w\s]*[0-9]{4}?", singleLineText)
        self.textSections.extend(sections)

    def parseSectionsCriminal(self):
        singleLineText = self.text.replace("\n", " ")
#         sections = re.findall("sections?\s*([0-9]+-?[a-zA-Z]?\/?)*",singleLineText)
        sections = re.findall(
            "sections?\s*([0-9]+-?[a-zA-Z]?\/?)*[\w\s]*((cr\.?p\.?c\.?)|i\.?p\.?c\.?|indian penal code|code of criminal procedure)", singleLineText)
        result_sections = []
        for i in range(0, len(sections)):
            li = list(sections[i])
            word = li[1]
            if re.match("((cr\.?p\.?c\.?)|code of criminal procedure)", word):
                li[1] = "crpc"
            if re.match("(i\.?p\.?c\.?|indian penal code)", word):
                li[1] = "ipc"
            li.pop()
            # sections[i] = "&".join(li)
            if(li[0].strip() != "" and li[1].strip() != ""):
                result_sections.append("-".join(li))
        self.sections.extend(list(set(result_sections)))

    def processDate(self, date: datetime):
        res = date.strftime("%m/%d/%Y")
        return res

    def getPetitionerAndRespondent(self):
        res = ""
        pet = ""
        for line in self.lines:
            if " vs " in line:
                splitted = line.split(" vs ")
                pet = splitted[0]
                res = splitted[1]
                return [pet, res]
        return [pet, res]

    def extractAllDates(self):
        matches = datefinder.find_dates(self.text)
        uniqueDates = list(set(map(self.processDate, matches)))
        return uniqueDates

    def extractDateParam(self, startFrom):
        pet_list = ""
        for i in range(0, len(self.lines)):
            line = self.lines[i]
            if(startFrom in line):
                pet_list = line
                break
        date_extract_pattern = "[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}"
        matchedDate = re.findall(date_extract_pattern, pet_list)
        return matchedDate

    def getLinesUntil(self, src_list, untilStringList, failsafeLineCount):
        result = []
        for i in range(0, failsafeLineCount):
            line = src_list[i]
            for word in untilStringList:
                if word in line:
                    return result
            result.append(line.strip())
        return []

    def extractParam(self, startFrom, untilStringList, failsafeLineCount):
        pet_list = []
        for i in range(0, len(self.lines)):
            line = self.lines[i]
            if(startFrom in line):
                pet_list.extend(self.getLinesUntil(
                    self.lines[i:], untilStringList, failsafeLineCount))
                return pet_list
        return pet_list

    def extract_before_keyword(self, keyword):
        for line in self.lines:
            if(keyword in line):
                temp_list = [line.strip().split('    ')[0]]
                return temp_list
        return []
