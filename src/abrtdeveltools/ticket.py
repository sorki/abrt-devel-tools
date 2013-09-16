class Ticket(object):
	def __init__(self, component, ticket_id, summary, assignee):
		self.component = component
		self.ticket_id = ticket_id
		self.summary = summary
		self.assignee = assignee

	def get_component(self):
		return self.component

	def get_id(self):
		return self.ticket_id

	def get_summary(self):
		return self.summary

	def get_assignee(self):
		return self.assignee