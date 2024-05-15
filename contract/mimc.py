import typing

import algopy as py
from algopy.arc4 import abimethod, baremethod, DynamicArray, StaticArray, Byte

Bytes32: typing.TypeAlias = StaticArray[Byte, typing.Literal[32]]

class Mimc(py.ARC4Contract):
	@baremethod(create='allow', allow_actions=['UpdateApplication', 'DeleteApplication', 'NoOp'])
	def barecall(self) -> None:
		True

	@abimethod
	def mimc_BN254(self, data: py.Bytes) -> Bytes32:
		# we use the sha opcode as a placeholder to make puyapy compile,
		# then we substitute it with the new mimc BN254g1 in the compiled teal
		result = py.op.sha256(data)
		return Bytes32.from_bytes(result)

	@abimethod
	def mimc_BLS12_381(self, data: py.Bytes) -> Bytes32:
		# we use the keccak opcode as a placeholder to make puyapy compile,
		# then we substitute it with the new mimc BLS12_381g1 in the compiled teal
		result = py.op.keccak256(data)
		return Bytes32.from_bytes(result)


