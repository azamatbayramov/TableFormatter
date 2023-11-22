from abc import ABC, abstractmethod
from typing import List
import numpy as np


HORIZONTAL_DELIMITER = "-"
VERTICAL_DELIMITER = "|"

"""
Table example:

-----------------------------------------------------
|        |           Destination           |        |
| Source |---------------------------------| Supply |
|        |  D1    D2     D3     D4     D5  |        |
|--------|---------------------------------|--------|
|   A1   | 2.0   3.0    4.0    2.0    4.0  | 140.0  |
|   A2   | 8.0   4.0    1.0    4.0    1.0  | 180.0  |
|   A3   | 9.0   7.0    3.0    7.0    2.0  | 160.0  |
|--------|---------------------------------|--------|
| Demand | 60.0  70.0  120.0  130.0  100.0 | 480.0  |
-----------------------------------------------------
"""


class Block(ABC):
    def __init__(self) -> None:
        self.width = self.get_min_width()
        self.height = self.get_min_height()

    @abstractmethod
    def get_min_width(self) -> int:
        pass

    @abstractmethod
    def get_min_height(self) -> int:
        pass

    def set_width(self, width: int) -> None:
        self.width = max(self.width, width)

    def set_height(self, height: int) -> None:
        self.height = max(self.height, height)

    @abstractmethod
    def get_formatted_list(self) -> List[str]:
        pass

    def __str__(self) -> str:
        return "\n".join(self.get_formatted_list())


class Element(Block):
    def __init__(self, text: str) -> None:
        self.text = text

        super().__init__()

    def get_min_width(self) -> int:
        return len(self.text) + 2

    def get_min_height(self) -> int:
        return 1

    def get_formatted_list(self) -> List[str]:
        result_lst = []

        indent_above = self.height // 2
        indent_under = self.height // 2

        if self.height % 2 != 1:
            indent_above -= 1

        result_lst += [" " * self.width for i in range(indent_above)]

        result_lst.append(self.text.center(self.width))

        result_lst += [" " * self.width for i in range(indent_under)]

        return result_lst


class HorizontalLine(Block):
    def get_min_width(self) -> int:
        return 0

    def get_min_height(self) -> int:
        return 1

    def get_formatted_list(self) -> List[str]:
        return [HORIZONTAL_DELIMITER * self.width]


class VerticalLine(Block):
    def get_min_width(self) -> int:
        return 1

    def get_min_height(self) -> int:
        return 0

    def get_formatted_list(self) -> List[str]:
        return [VERTICAL_DELIMITER] * self.height


class Column(Block):
    def __init__(self) -> None:
        self.blocks: List[Block] = []

        super().__init__()

    def add_block(self, block: Block) -> None:
        self.blocks.append(block)
        self.set_width(self.get_min_width())
        self.set_height(self.get_min_height())

    def get_min_width(self) -> int:
        if not self.blocks:
            return 0
        return max([e.get_min_width() for e in self.blocks])

    def get_min_height(self) -> int:
        if not self.blocks:
            return 0
        return sum([e.get_min_height() for e in self.blocks])

    def get_formatted_list(self) -> List[str]:
        result = []

        for block in self.blocks:
            block.set_width(self.width)
            result += block.get_formatted_list()

        return result


class Row(Block):
    def __init__(self) -> None:
        self.blocks: List[Block] = []

        super().__init__()

    def add_block(self, block: Block) -> None:
        self.blocks.append(block)
        self.set_width(self.get_min_width())
        self.set_height(self.get_min_height())

    def get_min_width(self) -> int:
        if not self.blocks:
            return 0
        return sum([e.get_min_width() for e in self.blocks])

    def get_min_height(self) -> int:
        if not self.blocks:
            return 0
        return max([e.get_min_height() for e in self.blocks])

    def get_formatted_list(self) -> List[str]:
        result = []

        for block in self.blocks:
            block.set_height(self.height)
            for i, line in enumerate(block.get_formatted_list()):
                if i >= len(result):
                    result.append(line)
                else:
                    result[i] += line

        return result


class TransportationProblemTableFormatter:
    def __init__(
        self, s_array: np.ndarray, c_array: np.ndarray, d_array: np.ndarray
    ) -> None:
        self.s_array: np.ndarray = s_array
        self.c_array: np.ndarray = c_array
        self.d_array: np.ndarray = d_array

        self.table: Block = None

    def _create_source_column(self) -> Column:
        source_column = Column()

        source_title = Element("Source")
        source_title.set_height(3)

        source_column.add_block(source_title)

        source_column.add_block(HorizontalLine())

        for i in range(len(self.s_array)):
            source_column.add_block(Element(f"A{i + 1}"))

        source_column.add_block(HorizontalLine())

        source_column.add_block(Element("Demand"))

        return source_column

    def _create_destination_table(self) -> Row:
        destination_columns = Row()

        for i in range(len(self.d_array)):
            destination_column = Column()

            destination_column.add_block(Element(f"D{i + 1}"))
            destination_column.add_block(HorizontalLine())

            for j in range(len(self.s_array)):
                destination_column.add_block(Element(str(self.c_array[j][i])))

            destination_column.add_block(HorizontalLine())
            destination_column.add_block(Element(str(self.d_array[i])))

            destination_columns.add_block(destination_column)

        destination_table = Column()

        destination_table.add_block(Element("Destination"))
        destination_table.add_block(HorizontalLine())
        destination_table.add_block(destination_columns)

        return destination_table

    def _create_supply_column(self) -> Column:
        supply_column = Column()

        supply_title = Element("Supply")
        supply_title.set_height(3)

        supply_column.add_block(supply_title)
        supply_column.add_block(HorizontalLine())

        for i in range(len(self.s_array)):
            supply_column.add_block(Element(str(self.s_array[i])))

        supply_column.add_block(HorizontalLine())
        supply_column.add_block(Element(str(sum(self.s_array))))

        return supply_column

    def _create_table(self) -> None:
        source_column = self._create_source_column()
        destination_table = self._create_destination_table()
        supply_column = self._create_supply_column()

        table = Row()

        table.add_block(VerticalLine())
        table.add_block(source_column)
        table.add_block(VerticalLine())
        table.add_block(destination_table)
        table.add_block(VerticalLine())
        table.add_block(supply_column)
        table.add_block(VerticalLine())

        table_with_horizontal_lines = Column()

        table_with_horizontal_lines.add_block(HorizontalLine())
        table_with_horizontal_lines.add_block(table)
        table_with_horizontal_lines.add_block(HorizontalLine())

        self.table = table_with_horizontal_lines

    def _format(self) -> None:
        self._create_table()

    def format(self) -> Block:
        self._format()

        return self.table
