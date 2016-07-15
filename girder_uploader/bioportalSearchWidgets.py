"""Includes bioportalSearchWidgets class.

bioportalSearchWidgets uses ipywidgets to create search boxes for the purpose
of collecting metadata via searching the Bioportal ontology API.

"""

import ipywidgets as widgets
import requests
from IPython.display import display


class BioportalSearchWidgets:
    """Uses ipwidgets to create search boxes.

    Provides a template for a search box and a results box.
    Connects to the bioportal REST API to return ontology information.

    Use of this class must adhear to a strict call order as follows.

    1) Initialize object to provide callback.
    2) add_search_widget, this may be called as many times as needed to
       add the necessary metadata collecting widgets.
    3) display_widgets, this displays the already created widgets which step
       2 created.

    """

    def __init__(self, submit_callback,
                 bioportal_api_key='efa3babf-b23c-4399-89f7-689bb9d576fb'):
        """Initialize variables, provide valid api key for bioportal.

        param: submit_callback: Callback to be executed on submit. The
               single parameter to the callback is a dictionary whose keys
               are the topics and whose values are a tuple in the form of
               (keyword, bioportal responses dictionary for that keyword).

        """
        self._search_widgets = dict()
        self._result_widgets = dict()
        self._ontologies = dict()
        self._results = dict()
        self._required_valid_results = dict()
        self._keywords = dict()
        self._required_widgets = []
        self._containers = []
        self._values = []
        self._submit_callback = submit_callback
        self._background_color = '#ffe6e6'
        self._apply_widget = None

        self._api_url = 'http://data.bioontology.org/'
        self._key = bioportal_api_key
        self._headers = {'Authorization': 'apikey token=' + self._key}

    def __request_suggestions(self, search_term, ontologies):
        """Search specified ontologies using bioportals REST API.

        Returns list of suggested keywords and a dictionary with the
        keywords as keys and bioportal response data as values.

        :param searchTerm: The term to search bioportal with.
        :param ontologies: A list of ontology IDs to search.

        """
        parameters = {'ontologies': ontologies,
                      'suggest': 'true', 'pagesize': 15}
        search = self._api_url + 'search?q=' + search_term

        data = self.GET(search, params=parameters)
        nameList = ['...']
        nameDict = {}
        if "collection" in data:
            collection = data["collection"]
        else:
            return (nameList, nameDict)

        for d in collection:
            nameDict[d["prefLabel"]] = d
            nameList.append(d["prefLabel"])

        return (nameList, nameDict)

    def GET(self, url, params=None):
        """Convenient method for requests.get().

        Headers already included in call. JSON response data is returned.

        :param url: The website to access JSON data from.
        :param params: Parameters for the REST request.

        """
        request = requests.get(url, headers=self._headers, params=params)
        return request.json()

    def add_search_widget(self, name, ontologies, required=False):
        """Create a new search widget and result widget.

        Create(but not display) a search widget and a corresponding results
        widget for the provided name. The widget searches through the
        specified ontologies and can be required before upload executes.

        param: name: Name of the desired metadata, e.g., disease, region, etc
        param: ontologies: List of ontology IDs to be searched.
        param: required: Whether or not to require this metadata before upload
                         or leave it optional.

        """
        self._ontologies[name] = ontologies

        input_widget = widgets.Text(description=name, value='')
        results_name = name + " results:"
        if required:
            input_widget.background_color = self._background_color
            self._required_widgets.append(results_name)
            self._required_valid_results[results_name] = False

        self._search_widgets[name] = input_widget

        results_widget = widgets.Select(options=['...'],
                                        description=results_name)
        self._result_widgets[results_name] = results_widget

        contains = [input_widget, results_widget]
        container = widgets.HBox(children=contains)
        self._containers.append(container)

    def __validate_apply(self):
        """Validate all required widgets before upload."""
        for entry in self._required_widgets:
                if not self._required_valid_results[entry]:
                    self._apply_widget.disabled = True
                    return
        self._apply_widget.disabled = False

    def display_widgets(self):
        """Display all created search and results widgets.

        Search widgets must be added prior to this call.

        """
        self._apply_widget = widgets.Button(description='Submit',
                                            disabled=True)

        for container in self._containers:
            display(container)
        display(self._apply_widget)

        def search_value_changed(change):
            """Update what is in the results widget when search is changed.

            Callback for value change in the search widget's search field.

            """
            widget_name = change['owner'].description
            widget_value = change['new'].strip()
            results_name = widget_name + " results:"
            if widget_value:
                ontologies = self._ontologies[widget_name]
                options, info = self.__request_suggestions(widget_value,
                                                           ontologies)
                if len(options) == 1:
                    tmp = ['...', 'NO RESULTS FOUND']
                    self._result_widgets[results_name].options = tmp
                    self._results.pop(widget_name, None)
                else:
                    self._results[widget_name] = info
                    self._result_widgets[results_name].options = options
            else:
                self._result_widgets[results_name].options = ['...']
                self._results.pop(widget_name, None)

        def results_value_selected(change):
            """Add selected result into a the keywords dictionary.

            Callback for value selected in result widget's selection field.

            """
            alert = "NO RESULTS FOUND"
            widget_name = change['owner'].description
            name = widget_name[0:-9]

            selected_value = self._result_widgets[widget_name].selected_label
            if selected_value != alert and selected_value != '...':
                self._values.append(selected_value)
                self._required_valid_results[widget_name] = True
                self._keywords[name] = selected_value
            else:
                self._required_valid_results[widget_name] = False
                self._results.pop(name, None)

            self.__validate_apply()

        def on_apply_clicked(change):
            """Callback for submit button click."""
            final_results = {}

            for topic in self._results:
                keyword = self._keywords[topic]
                final_results[topic] = (keyword,
                                        self._results[topic][keyword])

            self._submit_callback(final_results)

        for key in self._search_widgets:
            self._search_widgets[key].observe(search_value_changed,
                                              names='value')

        for key in self._result_widgets:
            self._result_widgets[key].observe(results_value_selected,
                                              names='selected_label')

        self._apply_widget.on_click(on_apply_clicked)
