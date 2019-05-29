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
                    "bill_number": bill_attrib["Bill_Number"],
                    "display_order": bill_attrib["Display_Order"],
                    "reconsidered": bill_attrib["Reconsidered"],
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
                "bill_number": bill_attrib["Bill_Number"],
                "display_order": bill_attrib["Display_Order"],
                "reconsidered": bill_attrib["Reconsidered"],
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
                    "bill_number": bill_attrib["Bill_Number"],
                    "display_order": bill_attrib["Display_Order"],
                    "reconsidered": bill_attrib["Reconsidered"],
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
                    "bill_number": bill_attrib["Bill_Number"],
                    "display_order": bill_attrib["Display_Order"],
                    "reconsidered": bill_attrib["Reconsidered"],
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

    def committees_by_leg_body(self, legislature_id: int, body: str):

        response = self.client.service.CommitteeByLegBody(legislature_id, body)

        meta = response.attrib

        committees = {"legislature_id": meta["legislature"], "committees": []}

        for type in response:

            committee_type = type.attrib["Committee_Type"]

            for body in type:

                committee_body = body.attrib["Body"]

                for committee in body:

                    committee_attrib = committee.attrib

                    current = {
                        "type": committee_type,
                        "body": committee_body,
                        "committee_id": committee_attrib["Committee_ID"],
                        "committee_name": committee_attrib["Committee_Name"],
                        "committee_short_name": committee_attrib[
                            "Committee_Short_Name"
                        ],
                        "sub_committee": committee_attrib["Sub_Committee"],
                    }

                    committees["committees"].append(current)

        return committees

    # Returns two body tags
    # Only get commitee data from body tags with children?

    def committee_by_leg_id(self, legislature_id: int, committee_id: int):

        response = self.client.service.CommitteeByLegID(legislature_id, committee_id)

        meta = response.attrib

        committees = {"legislature_id": meta["legislature"]}

        for committee_type in response:

            committee_type_str = committee_type.attrib["Committee_Type"]

            for committee_body in committee_type:

                committee_body_str = committee_body.attrib["Body"]

                for committee in committee_body:

                    committee_attrib = committee.attrib

                    obj = {
                        "type": committee_type_str,
                        "body": committee_body_str,
                        "committee_id": committee_attrib["Committee_ID"],
                        "committee_name": committee_attrib["Committee_Name"],
                        "committee_short_name": committee_attrib[
                            "Committee_Short_Name"
                        ],
                        "sub_committee": committee_attrib["Sub_Committee"],
                    }

                    committees["committee"] = obj

        return committees

    def committee_by_leg_type(self, legislature_id: int, committee_type: str) -> Dict:

        response = self.client.service.CommitteeByLegType(
            legislature_id, committee_type
        )

        meta = response.attrib

        committees = {"legislature_id": meta["legislature"], "committees": []}

        for type in response:

            committee_type = type.attrib["Committee_Type"]

            for body in type:

                committee_body = body.attrib["Body"]

                for committee in body:

                    committee_attrib = committee.attrib

                    current = {
                        "type": committee_type,
                        "body": committee_body,
                        "committee_id": committee_attrib["Committee_ID"],
                        "committee_name": committee_attrib["Committee_Name"],
                        "committee_short_name": committee_attrib[
                            "Committee_Short_Name"
                        ],
                        "sub_committee": committee_attrib["Sub_Committee"],
                    }

                    committees["committees"].append(current)

        return committees

    def committees_by_leg_type_body(self, legislature_id, body: str) -> Dict:

        response = self.client.service.CommitteeByLegBody(legislature_id, body)

        meta = response.attrib

        committees = {"legislature_id": meta["legislature"], "committees": []}

        for type in response:

            committee_type = type.attrib["Committee_Type"]

            for body in type:

                committee_body = body.attrib["Body"]

                for committee in body:

                    committee_attrib = committee.attrib

                    current = {
                        "type": committee_type,
                        "body": committee_body,
                        "committee_id": committee_attrib["Committee_ID"],
                        "committee_name": committee_attrib["Committee_Name"],
                        "committee_short_name": committee_attrib[
                            "Committee_Short_Name"
                        ],
                        "sub_committee": committee_attrib["Sub_Committee"],
                    }

                    committees["committees"].append(current)

        return committees

    def committees_by_leg(self, legislature_id: int) -> Dict:

        response = self.client.service.CommitteeByLegislature(legislature_id)

        meta = response.attrib

        committees = {"legislature_id": meta["legislature"], "committees": []}

        for type in response:

            committee_type = type.attrib["Committee_Type"]

            for body in type:

                committee_body = body.attrib["Body"]

                for committee in body:

                    committee_attrib = committee.attrib

                    current = {
                        "type": committee_type,
                        "body": committee_body,
                        "committee_id": committee_attrib["Committee_ID"],
                        "committee_name": committee_attrib["Committee_Name"],
                        "committee_short_name": committee_attrib[
                            "Committee_Short_Name"
                        ],
                        "sub_committee": committee_attrib["Sub_Committee"],
                    }

                    committees["committees"].append(current)

        return committees

    def committee_members(self, session_id: int, committee_id: int) -> Dict:

        response = self.client.service.CommitteeMembers(session_id, committee_id)

        current_body = response.find("BODY")
        current_committee = current_body.find("COMMITTEE")

        response_committee_id = current_committee.get("Committee_ID")

        committee_members = {
            "committee_id": response_committee_id,
            "committee_type": current_committee.get("Committee_Type"),
            "committee_name": current_committee.get("Committee_Name"),
            "committee_members": [],
        }

        # Probably a better way of doing this

        for body in response:
            for committee in body:
                for members in committee:
                    for member in members:
                        obj = {
                            "member_order": member.get("Member_Order"),
                            "member_id": member.get("Member_ID"),
                            "member_name": member.get("Member_Name"),
                            "member_position": member.get("Member_Position"),
                        }

                        committee_members["committee_members"].append(obj)

        return committee_members

    def documents_by_bill_num(self, session_id: int, bill_number: str):

        response = self.client.service.DocumentsByBillNum(session_id, bill_number)

        documents = {"bill_number": bill_number, "documents": []}

        for document in response:
            obj = {
                "item": document.get("Item"),
                "transaction_type": document.get("Transaction_Type"),
                "bill_number": document.get("Bill_Number"),
                "document_type": document.get("Document_Type"),
                "document_format": document.get("Document_Format"),
                "description": document.get("Description"),
                "url": document.get("URL"),
                "transaction_date": document.get("Transaction_Date"),
            }

            documents["documents"].append(obj)

        return documents

    def documents_by_bill_num_doc_type(
        self, session_id: int, bill_number: str, doc_type: str
    ):

        response = self.client.service.DocumentsByBillNumDocType(
            session_id, bill_number, doc_type
        )

        documents = {"bill_number": bill_number, "documents": []}

        for document in response:
            obj = {
                "item": document.get("Item"),
                "transaction_type": document.get("Transaction_Type"),
                "bill_number": document.get("Bill_Number"),
                "document_type": document.get("Document_Type"),
                "document_format": document.get("Document_Format"),
                "description": document.get("Description"),
                "url": document.get("URL"),
                "transaction_date": document.get("Transaction_Date"),
            }

            documents["documents"].append(obj)

        return documents

    def documents_by_doc_type(self, session_id: int, doc_type: str) -> Dict:

        response = self.client.service.DocumentsByDocType(session_id, doc_type)

        documents = {"session_id": session_id, "documents": []}

        for document in response:
            obj = {
                "item": document.get("Item"),
                "transaction_type": document.get("Transaction_Type"),
                "bill_number": document.get("Bill_Number"),
                "document_type": document.get("Document_Type"),
                "document_format": document.get("Document_Format"),
                "description": document.get("Description"),
                "url": document.get("URL"),
                "transaction_date": document.get("Transaction_Date"),
            }

            documents["documents"].append(obj)

        return documents

    def documents_by_session_id(self, session_id: int):

        response = self.client.service.DocumentsBySessionID(session_id)

        documents = {"session_id": session_id, "documents": []}

        for document in response:
            obj = {
                "item": document.get("Item"),
                "transaction_type": document.get("Transaction_Type"),
                "bill_number": document.get("Bill_Number"),
                "document_type": document.get("Document_Type"),
                "document_format": document.get("Document_Format"),
                "description": document.get("Description"),
                "url": document.get("URL"),
                "transaction_date": document.get("Transaction_Date"),
            }

            documents["documents"].append(obj)

        return documents

    def documents_from_date(self, session_id: int, start_date: str):

        response = self.client.service.DocumentsByBillNumFromDate(
            session_id, start_date
        )

        documents = {"session_id": session_id, "documents": []}

        for document in response:
            obj = {
                "item": document.get("Item"),
                "transaction_type": document.get("Transaction_Type"),
                "ill_number": document.get("Bill_Number"),
                "document_type": document.get("Document_Type"),
                "document_format": document.get("Document_Format"),
                "description": document.get("Description"),
                "url": document.get("URL"),
                "transaction_date": document.get("Transaction_Date"),
            }

            documents["documents"].append(obj)

        return documents

    # TODO Borked

    def documents_from_date_to_date(
        self, session_id: int, start_date: str, end_date: str
    ):

        response = self.client.service.DocumentsFromDateToDate(
            session_id, start_date, end_date
        )

        documents = {"session_id": session_id, "documents": []}

        for document in response:
            obj = {
                "item": document.get("Item"),
                "transaction_type": document.get("Transaction_Type"),
                "bill_number": document.get("Bill_Number"),
                "document_type": document.get("Document_Type"),
                "document_format": document.get("Document_Format"),
                "description": document.get("Description"),
                "url": document.get("URL"),
                "transaction_date": document.get("Transaction_Date"),
            }

            documents["documents"].append(obj)

        return documents

    def exe_nom_current_position_holder(
        self, session_id: int, agency_id: int, position_id: int
    ) -> Dict:

        response = self.client.service.ExeNomCurrentPositionHolder(
            session_id, agency_id, position_id
        )

        nominee_position = response.find("NOMINEEPOS")

        nominee = {
            "agency_id": nominee_position.get("AgencyId"),
            "position_id": nominee_position.get("PositionId"),
            "nominee_id": nominee_position.get("NomineeId"),
            "first_name": nominee_position.get("FirstName"),
            "middle_initial": nominee_position.get("MiddleInitial"),
            "last_name": nominee_position.get("LastName"),
            "title": nominee_position.get("Title"),
            "party": nominee_position.get("Party"),
            "nominee_position_id": nominee_position.get("NomineePositionId"),
            "received_date": nominee_position.get("ReceivedDate"),
            "confirmed_date": nominee_position.get("ConfirmedDate"),
            "governor": nominee_position.get("Governor"),
            "position_comment": nominee_position.get("PositionComment"),
            "replacing": nominee_position.get("Replacing"),
            "appointment_date": nominee_position.get("AppointmentDate"),
            "expiration_date": nominee_position.get("ExpirationDate"),
            "caucus_date": nominee_position.get("CaucusDate"),
            "gov_notified_date": nominee_position.get("GovNotifiedDate"),
            "withdrawn_from_consideration": nominee_position.get(
                "WithdrawnFromConsideration"
            ),
            "comments": nominee_position.get("Comments"),
            "reappoint": nominee_position.get("Reappoint"),
            "no_longer_serving": nominee_position.get("NoLongerServing"),
            "wo_conf": nominee_position.get("WOConf"),
            "wd_date": nominee_position.get("WDDate"),
        }

        return nominee

    def exe_nom_by_id(self, nominee_id: int):

        response = self.client.service.ExeNomNomineeById(nominee_id)

        nominee = response.find("NOMINEE")
        nominee_position = nominee.find("NOMPOSITION")

        obj = {
            "nominee_id": nominee.get("NomineeId"),
            "first_name": nominee.get("FirstName"),
            "middle_initial": nominee.get("MiddleInitial"),
            "last_name": nominee.get("LastName"),
            "title": nominee.get("Title"),
            "party": nominee.get("Party"),
            "address_line_1": nominee.get("AddressLine1"),
            "address_line_2": nominee.get("AddressLine2"),
            "address_line_3": nominee.get("AddressLine3"),
            "nominee_dosition_Id": nominee_position.get("NomineePositionId"),
            "received_date": nominee_position.get("ReceivedDate"),
            "confirmed_date": nominee_position.get("ConfirmedDate"),
            "governor": nominee_position.get("Governor"),
            "position_comment": nominee_position.get("PositionComment"),
            "replacing": nominee_position.get("Replacing"),
            "appointment_date": nominee_position.get("AppointmentDate"),
            "expiration_date": nominee_position.get("ExpirationDate"),
            "referred_date": nominee_position.get("ReferredDate"),
            "report_date": nominee_position.get("ReportDate"),
            "caucus_date": nominee_position.get("CaucusDate"),
            "committee_Short_Name": nominee_position.get("CommitteeShortName"),
            "gov_notified_date": nominee_position.get("GovNotifiedDate"),
            "withdrawn_from_consideration": nominee_position.get(
                "WithdrawnFromConsideration"
            ),
            "comments": nominee_position.get("Comments"),
            "reappoint": nominee_position.get("Reappoint"),
            "caucus_vote": nominee_position.get("CaucusVote"),
            "beginning_date": nominee_position.get("BeginningDate"),
            "no_longer_serving": nominee_position.get("NoLongerServing"),
            "wd_date": nominee_position.get("WDDate"),
        }

        return obj

    def exec_nom_agencies_and_positions(self, include_disabled_agencies: int):

        response = self.client.service.ExecNomAgenciesandPositions(include_disabled_agencies)

        agencies = {
            "agencies":[]
        }

        for agency in response:
            
            agency_obj = {
                "agency_id":agency.get("AgencyID"),
                "agency_name":agency.get("AgencyName"),
                "proper_name":agency.get("ProperName"),
                "origin":agency.get("Origin"),
                "term_length":agency.get("TermLength"),
                "description":agency.get("Description"),
                "disabled":agency.get("Disabled"),
                "positions":[]
            }

            for position in agency:
                position_obj = {
                    "position_id":position.get("PositionId"),
                    "name":position.get("Name"),
                    "display_order":position.get("DisplayOrder"),
                    "disabled":position.get("Disabled")
                }

                agency_obj["positions"].append(position_obj)

            agencies["agencies"].append(agency_obj)

        return agencies

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
    # TODO Does not work ... ?

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
