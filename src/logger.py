from typing import Any, Final, Literal, Optional, Tuple
from datetime import datetime
from rich.pretty import pprint

Color = Literal['black', 'gray', 'white', 'red', 'yellow', 'green', 'lightblue', 'blue', 'purple', 'pink']
colors: dict[Color, str] = {
	'black': '#232323',
	'white': '#cecece',
	'gray': '#848484',
	'red': '#ef8d77',
	'yellow': '#efe777',
	'green': '#79ef77',
	'lightblue': '#4f5975',
	'blue': '#77b5ef',
	'purple': '#c777ef',
	'pink': '#ef77df',
}

class Logger():
	RESET: Final[str] = '\033[0m'

	def __init__(self, name: str = 'MAIN'):
		self.name = name

	@staticmethod
	def fetchTime(format: str = '[%H:%M:%S]') -> str:
		"""
		Function to fetch the current date, and return it in a given format

		Args:
			format (str, optional): The format string to call strftime with. Defaults to '[%H:%M:%S]'.

		Returns:
			str: The formatted time string
		"""

		date = datetime.now()
		return date.strftime(format)

	@staticmethod
	def hexToAnsi(hex: str, is_background: Optional[bool]) -> str:
		"""
		Function to convert a hex color string to an ANSI color code

		Args:
			`hex (str)`: The hex color string to convert
			`is_background` (Optional[bool]): _description_

		Returns:
			`str`: The ANSI color code
		"""

		r = int(hex[1:3], 16)
		g = int(hex[3:5], 16)
		b = int(hex[5:7], 16)

		if is_background:
			return f'\033[48;2;{r};{g};{b}m'
		else:
			return f'\033[38;2;{r};{g};{b}m'

	def _log(
		self,
		_color: Color,
		args: Tuple[Any]
	) -> None:
		color = self.hexToAnsi(colors[_color], True)
		date = self.fetchTime()
		print(f'{date} {color} {self.RESET} [{self.name}]', end=' ')
		for arg in args:
			if isinstance(arg, str): # we want to print strings on the same line as the main text, and anything else below
				print(arg)
			else:
				pprint(arg, expand_all=True)

	def info(
		self,
		*args: Any
	):
		self._log('lightblue', args)

	def error(
		self,
		*args: Any
	):
		self._log('red', args)

	def warn(
		self,
		*args: Any
	):
		self._log('yellow', args)

	def success(
		self,
		*args: Any
	):
		self._log('green', args)