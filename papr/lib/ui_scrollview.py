# The last element is selected at the beginning.
class ScrollView:
    def __init__(self, n_elements, rows, selected):
        self.n_elemens = n_elements
        self._rows = rows
        self._selected = selected    # selected is in [0..n_elements-1]
        self.first_element_in_view = max(0, n_elements - rows)

    def up(self):
        if self.first_element_in_view == self._selected:
            self.first_element_in_view = max(self.first_element_in_view - 1, 0)
        self._selected = max(0, self._selected - 1)

    def down(self):
        if self._selected == self.first_element_in_view + self._rows - 1:
            self.first_element_in_view = min(self.first_element_in_view + 1, self.n_elemens - self._rows)
        self._selected = min(self._selected + 1, self.n_elemens - 1)

    def selected(self):
        return self._selected

    def first(self):
        return self.first_element_in_view

    def end(self):
        return self.first_element_in_view + self._rows

    def rows(self):
        return self._rows