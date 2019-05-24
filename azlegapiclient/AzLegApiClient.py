from zeep import CachingClient
from zeep.wsse.username import UsernameToken
from lxml import objectify, etree
from typing import List, Dict
from enum import Enum
import isodate

WSDL = "https://www.azleg.gov/xml/legservice.asmx?WSDL"
DEBUG = 1


class AzLegApiClient:
    def __init__(self, username, password):
        self.client = CachingClient(
            WSDL, wsse=UsernameToken(username=username, password=password)
        )

    # def pretty_print_xml(self, node):
    #     print(etree.tostring(node, pretty_print=True))

    def iso_date(self, key: str, obj: object):
        return isodate.parse_datetime(obj[key]) if key in obj else None

    def ars(self):
        ars = self.client.service.ARS()
        for ars_document in ars:
            print(ars_document.attrib)

    # TODO Check what S Committee Type actually means

    CommitteeType = Enum("CommitteeType", [("Sitting", "S"), ("Financial", "F")])

    # Date

    def agendas_by_committee_id(self, session_id, committee_id, start_date=None):

        if start_date is not None:
            self.client.service.AgendaByCommitteeIDFromDate(
                session_id, committee_id, start_date
            )
        else:
            self.client.service.AgendaByCommitteeID(session_id, committee_id)

    def agenda_by_id(self, agenda_id):
        pass

    # Date

    def agendas_by_session_id(self, session_id, start_date=None):

        if start_date is not None:
            self.client.service.AgendaBySessionID(session_id)
        else:
            self.client.service.AgendaBySessionIDFromDate(session_id, start_date)

    # BillInfo

    def bill_info(self, session_id: int, bill_num: str) -> Dict:

        response = self.client.service.BillInfo(session_id, bill_num)

        current = response.find("BILL")
        sponsors = current.find("SPONSORS")
        docs = current.find("DOCS")
        meta = current.attrib

        bill = {
            "session_id": meta["Session_ID"],
            "bill_number": meta["Bill_Number"],
            "short_title": current.findtext("Short_Title"),
            "introduced_date": current.findtext("Introduced_Date"),
            "house_1st_read": current.findtext("House_1st_Read"),
            "house_official": current.findtext("House_Official"),
            "house_2nd_read": current.findtext("House_2nd_Read"),
            "house_consent_calendar_object": current.findtext(
                "House_Consent_Calendar_Object"
            ),
            "senate_official": current.findtext("Senate_Official"),
            "senate_consent_calendar_object": current.findtext(
                "Senate_Consent_Calendar_Object"
            ),
            "postingsheet": current.findtext("PostingSheet"),
            "last_updated": current.findtext("Last_Updated"),
            "sponsors": [],
            "docs": [],
        }

        for sponsor in sponsors:

            current = sponsor.attrib

            obj = {
                "display_order": current["Display_Order"],
                "type": current["Type"],
                "member_id": current["Member_ID"],
                "member_name": current["Member_Name"],
            }

            bill["sponsors"].append(obj)

        for doc in docs:

            current = doc.attrib

            obj = {
                "document_yype": current["Document_Type"],
                "document_format": current["Document_Format"],
                "description": current["Description"],
                "last_updated": current["Last_Updated"],
                "url": current["URL"],
            }

            bill["docs"].append(obj)

        return bill

    # BillsBySessionId

    def bills_by_session_id(self, session_id: int) -> Dict:

        response = self.client.service.BillsBySessionID(session_id)
        meta = response.attrib

        bills = {"session_id": meta["SessionID"], "bills": []}

        for bill in response:

            obj = {
                "bill_number": bill.findtext("Bill_Number"),
                "initial_title": bill.findtext("Initial_Title"),
                "current_title": bill.findtext("Current_Title"),
                "last_updated": isodate.parse_datetime(bill.findtext("Last_Updated")),
            }

            bills["bills"].append(obj)

        return bills

    # BillsUpdated

    def updated_bills(self, session_id: int, start_date: str):

        response = self.client.service.BillsUpdated(session_id, start_date)

        meta = response.attrib

        bills = {"session_id": meta["SessionID"], "bills": []}

        for bill in response:

            obj = {
                "bill_number": bill.findtext("Bill_Number"),
                "initial_title": bill.findtext("Initial_Title"),
                "current_title": bill.findtext("Current_Title"),
                "last_updated": isodate.parse_datetime(bill.findtext("Last_Updated")),
            }

            bills["bills"].append(obj)

        return bills

    def calendars_by_body(self, session_id: int, body: str) -> Dict:

        response = self.client.service.CalendarsByBody(session_id, body)

        calendars = {"session_id": session_id, "body": body, "calendars": []}

        for calendar in response:

            current = calendar.attrib

            calendar_obj = {
                "calendar_id": current["Cal_ID"],
                "body": current["Body"],
                "type": current["Type"],
                "calendar_date": current["Cal_Date"],
                "number": current["Number"],
                "committee_name": current["Committee_Name"],
                "committee_id": current["Committee_ID"],
                "calendar_name": current["Cal_Name"],
                "calendar_Time": current["Cal_Time"],
                "protest_date": current["Protest_Date"]
                if "Protest_Date" in current
                else None,
                "url": current["URL"] if "URL" in current else None,
                "bills": [],
            }

            for bill in calendar:

                bill_attrib = bill.attrib

                bill_obj = {
                    "Bill_Number": bill_attrib["Bill_Number"],
                    "Display_Order": bill_attrib["Display_Order"],
                    "Reconsidered": bill_attrib["Reconsidered"],
                }

                calendar_obj["bills"].append(bill_obj)

            calendars["calendars"].append(calendar_obj)

        return calendars

    def calendars_by_id(self, calendar_id):

        response = self.client.service.CalendarsByCalendarID(calendar_id)

        current = response.find("CALENDAR")
        current_attrib = current.attrib

        calendar = {
            "calendar_id": current_attrib["Cal_ID"],
            "body": current_attrib["Body"],
            "type": current_attrib["Type"],
            "calendar_date": current_attrib["Cal_Date"],
            "number": current_attrib["Number"],
            "committee_name": current_attrib["Committee_Name"],
            "committee_id": current_attrib["Committee_ID"],
            "calendar_name": current_attrib["Cal_Name"],
            "calendar_time": current_attrib["Cal_Time"],
            "protest_date": current_attrib["Protest_Date"],
            "url": current_attrib["URL"] if "URL" in current_attrib else None,
            "bills": [],
        }

        for bill in current:

            bill_attrib = bill.attrib

            bill_obj = {
                "Bill_Number": bill_attrib["Bill_Number"],
                "Display_Order": bill_attrib["Display_Order"],
                "Reconsidered": bill_attrib["Reconsidered"],
            }

            calendar["bills"].append(bill_obj)

        return calendar

    def calendars_by_committee_id(self, session_id, committee_id):

        response = self.client.service.CalendarsByCommittee(session_id, committee_id)

        calendars = {
            "session_id": session_id,
            "committee_id": committee_id,
            "calendars": [],
        }

        for calendar in response:

            current = calendar.attrib

            calendar_obj = {
                "calendar_id": current["Cal_ID"],
                "body": current["Body"],
                "type": current["Type"],
                "calendar_date": current["Cal_Date"],
                "number": current["Number"],
                "committee_name": current["Committee_Name"],
                "committee_id": current["Committee_ID"],
                "calendar_name": current["Cal_Name"],
                "calendar_Time": current["Cal_Time"],
                "protest_date": current["Protest_Date"],
                "url": current["URL"] if "URL" in current else None,
                "bills": [],
            }

            for bill in calendar:

                bill_attrib = bill.attrib

                bill_obj = {
                    "Bill_Number": bill_attrib["Bill_Number"],
                    "Display_Order": bill_attrib["Display_Order"],
                    "Reconsidered": bill_attrib["Reconsidered"],
                }

                calendar_obj["bills"].append(bill_obj)

            calendars["calendars"].append(calendar_obj)

        return calendars

    def calendars_by_session_id(self, session_id, start_date=None):

        if start_date is not None:
            response = self.client.service.CalendarsFromDate(session_id, start_date)
        else:
            response = self.client.service.CalendarsBySessionID(session_id)

        calendars = {"session_id": session_id, "calendars": []}

        for calendar in response:

            current = calendar.attrib

            calendar_obj = {
                "calendar_id": current["Cal_ID"],
                "body": current["Body"],
                "type": current["Type"],
                "calendar_date": current["Cal_Date"],
                "number": current["Number"],
                "committee_name": current["Committee_Name"],
                "committee_id": current["Committee_ID"],
                "calendar_name": current["Cal_Name"],
                "calendar_Time": current["Cal_Time"],
                "protest_date": current["Protest_Date"]
                if "Protest_Date" in current
                else None,
                "url": current["URL"] if "URL" in current else None,
                "bills": [],
            }

            for bill in calendar:

                bill_attrib = bill.attrib

                bill_obj = {
                    "Bill_Number": bill_attrib["Bill_Number"],
                    "Display_Order": bill_attrib["Display_Order"],
                    "Reconsidered": bill_attrib["Reconsidered"],
                }

                calendar_obj["bills"].append(bill_obj)

            calendars["calendars"].append(calendar_obj)

        return calendars

    def committee_actions(self, body=None, committee_type=None) -> List:
        if body is not None and committee_type is not None:
            response = self.client.service.CommitteeActionsQualified(
                body, committee_type
            )
        else:
            response = self.client.service.CommitteeActions()

        actions = []

        for action in response:

            current = action.attrib

            obj = {
                "action_id": current["Action_ID"],
                "action": current["Action"],
                "action_description": current["Action_Description"],
                "rfeir_action": current["RFEIR_Action"],
                "body": current["Body"],
                "committee_type": current["Committee_Type"],
            }

            actions.append(obj)

        return actions

    def committees_by_leg_body(self):
        pass

    def committees_by_leg_id(self):
        pass

    def committees_by_leg_type(self):
        pass

    def committees_by_leg_type_body(self):
        pass

    def committees_by_leg(self):
        pass

    def committee_members(self):
        pass

    def documents_by_bill_num(self):
        pass

    def documents_by_bill_num_doc_type(self):
        pass

    def documents_by_doc_type(self):
        pass

    def documents_from_date(self):
        pass

    def documents_from_date_to_date(self):
        pass

    def exe_nom_current_position_holder(self):
        pass

    def exe_nom_by_id(self):
        pass

    def exec_nom_a_and_p(self):
        pass

    def floor_votes_by_bill(self, session_id: int, bill_number: str) -> Dict:

        response = self.client.service.FloorVotesByBill(session_id, bill_number)

        meta = response.attrib

        votes = {"session_id": meta["SessionID"], "tran": []}

        for tran in response:

            tran_meta = tran.attrib

            tran_obj = {
                "tran_id": tran_meta["ID"],
                "type": tran_meta["Type"],
                "bill": tran_meta["Bill"],
                "cmte_id": tran_meta["CmteID"],
                "cmte_name": tran_meta["CmteName"],
                "cmte_short_name": tran_meta["CmteShortName"],
                "referral": tran_meta["Referral"],
                "cow_referral": tran_meta["COW_Referral"],
                "action": tran_meta["Action"],
                "action_id": tran_meta["Action_ID"],
                "action_date": tran_meta["ActionDate"],
                "comments": tran_meta["Comments"],
                "votes": [],
            }

            for vote in tran:

                current = vote.attrib

                vote_obj = {
                    "member_id": current["MemID"],
                    "member_name": current["MemName"],
                    "display_order": current["DisplayOrder"],
                    "vote": current["Vote"],
                }

                tran_obj["votes"].append(vote_obj)

            votes["tran"].append(tran_obj)

        return votes

    def floor_votes_by_bill_from_date(self):
        pass

    def floor_votes_by_committee_id(self):
        pass

    def floor_votes_by_session_id(self):
        pass

    def floor_votes_from_date(self):
        pass

    def floor_votes_from_date_to_date(self):
        pass

    def floor_votes_by_date(self):
        pass

    def bill_positions_by_date(self):
        pass

    def bill_positions_by_session(self):
        pass

    def bill_positions_by_session_from_date(self):
        pass

    def member_by_id(self, member_id: int, session_id: int):

        response = self.client.service.MemberByID()

        current = dict(response.attrib)

        member = {
            "legislature": current["Legislature"],
            "member_id": current["Member_ID"],
            "full_name": current["Full_Name"],
            "report_name": current["Report_Name"],
            "body": current["Body"],
            "district": current["District"],
            "party": current["Party"],
            "status": current["Status"],
            "postition": current["Postition"],
            "email": current["Email"],
            "phone": current["Phone"],
            "fax": current["Fax"],
            "maj_leader": current["Maj_Leader"],
            "min_leader": current["Min_Leader"],
            "maj_whip": current["Maj_Whip"],
            "min_whip": current["Min_Whip"],
            "room": current["Room"],
        }

        return member

    # TODO Test This One

    def member_committees(self, session_id: int, member_id: int) -> Dict:

        # response = self.client.service.MemberCommittees(session_id, member_id)

        pass

    def members_by_session_id(self, session_id: int) -> Dict:

        response = self.client.service.MembersBySessionID(session_id)

        members = {"session_id": session_id, "members": []}

        for current in response:

            member = {
                "legislature": current["Legislature"],
                "member_id": current["Member_ID"],
                "full_name": current["Full_Name"],
                "report_name": current["Report_Name"],
                "body": current["Body"],
                "district": current["District"],
                "party": current["Party"],
                "status": current["Status"],
                "postition": current["Postition"],
                "email": current["Email"],
                "phone": current["Phone"],
                "fax": current["Fax"],
                "maj_leader": current["Maj_Leader"],
                "min_leader": current["Min_Leader"],
                "maj_whip": current["Maj_Whip"],
                "min_whip": current["Min_Whip"],
                "room": current["Room"],
            }

            members["members"].append(member)

        return members

    def sessions(self):

        response = self.client.service.Sessions()

        sessions = []

        for session in response:

            current = dict(session.attrib)

            obj = {
                "session_id": current["Session_ID"],
                "session_full_name": current["Session_Full_Name"],
                "legislature": current["Legislature"],
                "session": current["Session"],
                "legislation_Year": current["Legislation_Year"],
                "session_start_date": isodate.parse_datetime(
                    current["session_start_date"]
                )
                if "session_start_date" in current
                else None,
                "sine_die_sate": isodate.parse_datetime(current["sine_die_date"])
                if "sine_die_date" in current
                else None,
            }

            sessions.append(obj)

        return sessions

    def session_by_id(self, session_id):

        response = self.client.service.SessionsbyID(session_id)

        current = dict(response.find("SESSION").attrib)

        session = {
            "session_id": current["Session_ID"],
            "session_full_name": current["Session_Full_Name"],
            "legislature": current["Legislature"],
            "session": current["Session"],
            "legislation_Year": current["Legislation_Year"],
            "session_start_date": isodate.parse_datetime(current["Session_Start_Date"])
            if "session_start_date" in current
            else None,
            "sine_die_sate": isodate.parse_datetime(current["Sine_Die_Date"])
            if "sine_die_date" in current
            else None,
        }

        return session

    def sponsored_bills(self, session_id, member_id):

        response = self.client.service.SponsoredBills(session_id, member_id)

        data = {"member": {}, "bills": []}

        sponsor = response.find("SPONSOR")

        member = dict(sponsor.attrib)

        data["member"] = {"name": member["MEMBER"], "member_id": member["MEMBER_ID"]}

        for bill in sponsor:

            bill = {
                "bill_number": bill.findtext("Bill_Number"),
                "sponsor_type": bill.findtext("Sponsor_Type"),
                "display_order": bill.findtext("Display_Order"),
                "bill_version": bill.findtext("Bill_Version"),
            }

            data["bills"].append(bill)

        return data

    def standing_by_bill_num(self):
        pass

    # TODO DATE

    def standing_by_committee(self, committee_id, start_date=None):
        pass

    def standing_by_session(self):
        pass

    def standing_from_date(self):
        pass

    def standing_vote_for_bill(self, session_id, bill_num):
        pass

    # TODO Date

    def standing_vote_by_committee(self, session_id, committee_id, date=None):
        pass

    def standing_vote_on_date(self, date):
        pass

    def standing_from_date_to_date(self, start_date, end_date):
        pass

    def videos_by_date(self, date):
        pass

    def videos_by_session(self, session_id):
        pass
