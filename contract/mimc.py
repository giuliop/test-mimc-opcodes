import typing

import algopy as py
from algopy.arc4 import abimethod, baremethod, DynamicArray, StaticArray, Byte

Bytes32: typing.TypeAlias = StaticArray[Byte, typing.Literal[32]]

class Mimc(py.ARC4Contract):
	@baremethod(create='allow', allow_actions=['UpdateApplication', 'DeleteApplication', 'NoOp'])
	def barecall(self) -> None:
		True

	@abimethod
	def mimc_BN254(self, data: DynamicArray[Bytes32]) -> Bytes32:
		tohash = py.Bytes()
		for i in py.urange(data.length):
			tohash += data[i].bytes
		# we use the sha opcode as a placeholder to make puyapy compile,
		# then we substitute it with the new mimc_BN254 in the compiled teal
		result = py.op.sha256(tohash)
		return Bytes32.from_bytes(result)

	@abimethod
	def mimc_BLS12_381(self, data: DynamicArray[Bytes32]) -> Bytes32:
		tohash = py.Bytes()
		for i in py.urange(data.length):
			tohash += data[i].bytes
		# we use the keccak opcode as a placeholder to make puyapy compile,
		# then we substitute it with the new mimc_BLS12_381 in the compiled teal
		result = py.op.keccak256(tohash)
		return Bytes32.from_bytes(result)


