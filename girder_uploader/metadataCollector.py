import ipywidgets as widgets
from IPython.display import display

class MetadataCollector:
    def __init__(self, topic, ontologies, required=False):
        self._required = required
        self._ontologies = ontologies
        # self._results_info stores keywords as keys and bioportal
        # results as values
        self._restuls_info = dict()
        # self._final_results stores only the info for added words
        self._final_restuls = dict()
        self._selected = None
        self._ready = False

        results_name = topic + " results:"
        self._search_input_widget = widgets.Text(description=topic,
                                           value='', width='100%')
        self._search_results_widget = widgets.Select(description=results_name,
                                               options=['...'],
                                               width='300')
        self._added_word_widget = widgets.Select(description='selected words:',
                                           width='300')
        self._add_button = widgets.Button(description='add', width='100%')
        self._remove_button = widgets.Button(description='remove',
                                             width='100%')

        search_contains = [self._search_input_widget]
        button_contains = [self._add_button, rself._emove_button]
        botton_container = widgets.VBox(children=button_contains)
        bottom_contains = [self._search_results_widget, bottom_container,
                           self._added_word_widget]
        bottom_container = widgets.HBoc(children=bottom_contains)

        self._container = widgets.VBox(children=[input_container,
                                                 bottom_container])]

    def display(self):
        display(self._container)
        self._search_input_widget.observe(self.__search_value_changed,
                                          names='value')
        self._search_results_widget.observe(self.__results_value_change,
                                            names='selected_value')

    def get_results(self):
        return self._results_info

    def __search(self, search_term, ontologies):
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

    def __search_value_changed(self, change):
        new_keyword = change['new'].strip()
        if new_keyword:
            keywords, info = self._search(new_keyword, self._ontologies)
            if len(keywords) == 1:
                temp = ['...', 'NO RESULTS FOUND']
                self._search_results_widget.options = temp
            else:
                self._search_results_widget.options = keywords
                self._restuls_info = info

    def __results_value_change(self, change):
        self._selected = _search_results_widget.selected_label

    def __add_button_click(self, change):
        self._restuls[self._selected] = self._results_info[self._selected]
        self._added_word_widget.options.append(self._selected)
        self._ready = True

    def __remove_button_click(self, change):
        selected = self._added_word_widget.selected_label
        self._results_info.pop(selected, None)
        if len(self._results_info) == 0:
            self._ready = False





