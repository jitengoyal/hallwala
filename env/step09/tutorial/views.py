import colander
import deform.widget

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.view import view_config

from .models import pages


class WikiPage(colander.MappingSchema):
	title = colander.SchemaNode(colander.String())
	body = colander.SchemaNode(colander.String(),widget=deform.widget.RichTextWidget())


class WikiViews(object):
	def __init__(self, request):
		self.request = request
		renderer = get_renderer("templates/layout.pt")
		self.layout = renderer.implementation().macros['layout']

	@reify
	def wiki_form(self):
		schema = WikiPage()
		return deform.Form(schema, buttons=('submit',))

	@reify
	def reqts(self):
		return self.wiki_form.get_widget_resources()

	@view_config(route_name='wiki_view',renderer='templates/wiki_view.pt')
	def wiki_view(self):
		return dict(title='Welcome to the Wiki',pages=pages.values())

	@view_config(route_name='wikipage_add',renderer='templates/wikipage_addedit.pt')
	def wikipage_add(self):
		form = self.wiki_form.render()

		if 'submit' in self.request.params:
			controls = self.request.POST.items()
			try:
				appstruct = self.wiki_form.validate(controls)
			except deform.ValidationFailure as e:
			# Form is NOT valid
				return dict(title='Add Wiki Page', form=e.render())

			# Form is valid, make a new identifier and add to list
			last_uid = int(sorted(pages.keys())[-1])
			new_uid = str(last_uid + 1)
			pages[new_uid] = dict(uid=new_uid, title=appstruct['title'],body=appstruct['body'])

			# Now visit new page
			url = self.request.route_url('wikipage_view', uid=new_uid)
			return HTTPFound(url)

		return dict(title='Add Wiki Page', form=form)

	@view_config(route_name='wikipage_view',renderer='templates/wikipage_view.pt')
	def wikipage_view(self):
		uid = self.request.matchdict['uid']
		page = pages[uid]
		return dict(page=page, title=page['title'])

	@view_config(route_name='wikipage_edit',renderer='templates/wikipage_addedit.pt')
	def wikipage_edit(self):
		uid = self.request.matchdict['uid']
		page = pages[uid]
		title = 'Edit ' + page['title']

		wiki_form = self.wiki_form

		if 'submit' in self.request.params:
			controls = self.request.POST.items()
			try:
				appstruct = wiki_form.validate(controls)
			except deform.ValidationFailure as e:
				return dict(title=title, page=page, form=e.render())

	# Change the content and redirect to the view
			page['title'] = appstruct['title']
			page['body'] = appstruct['body']

			url = self.request.route_url('wikipage_view',uid=page['uid'])
			return HTTPFound(url)

		form = wiki_form.render(page)

		return dict(page=page, title=title, form=form)

	@view_config(route_name='wikipage_delete')
	def wikipage_delete(self):
		uid = self.request.matchdict['uid']
		del pages[uid]

		url = self.request.route_url('wiki_view')
		return HTTPFound(url)