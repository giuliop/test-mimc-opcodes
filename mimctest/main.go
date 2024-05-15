package main

import (
	"encoding/hex"
	"fmt"
	"math/big"

	"github.com/consensys/gnark-crypto/ecc"
	"github.com/consensys/gnark/frontend"
	"github.com/consensys/gnark/std/hash/mimc"
	ap "github.com/giuliop/algoplonk"
	"github.com/giuliop/algoplonk/setup"
)

func main() {
	for _, curve := range []ecc.ID{ecc.BN254, ecc.BLS12_381} {
		ccOneInput, err := ap.Compile(&CircuitOneInput{}, curve, setup.Trusted)
		if err != nil {
			panic(err)
		}
		ccThreeInputs, err := ap.Compile(&CircuitThreeInputs{}, curve,
			setup.Trusted)
		if err != nil {
			panic(err)
		}

		curveIndex := 0
		if curve == ecc.BLS12_381 {
			curveIndex = 1
		}
		for _, test := range tests {
			if len(test.preimages) == 1 {
				assignment := &CircuitOneInput{Secret: test.preimages[0].Bytes(),
					Hash: test.hashCheck[curveIndex].value.Bytes()}
				_, err := ccOneInput.Verify(assignment)
				if err != nil {
					panic(err)
				}
			} else if len(test.preimages) == 3 {
				assignment := &CircuitThreeInputs{Secret1: test.preimages[0].Bytes(),
					Secret2: test.preimages[1].Bytes(),
					Secret3: test.preimages[2].Bytes(),
					Hash:    test.hashCheck[curveIndex].value.Bytes()}
				_, err := ccThreeInputs.Verify(assignment)
				if err != nil {
					panic(err)
				}
			} else {
				panic("unsupported number of preimages")
			}
		}
	}
}

type ValueWithBase struct {
	value string
	base  int
}
type HashCheck struct {
	curve ecc.ID
	value ValueWithBase
}
type Test struct {
	preimages []ValueWithBase
	hashCheck [2]HashCheck
}

func (v ValueWithBase) Bytes() []byte {
	if v.base == 16 {
		byteSlice, err := hex.DecodeString(v.value)
		if err != nil {
			fmt.Println("error decoding hex string: ", v.value)
			panic(err)
		}
		return byteSlice
	}
	if v.base == 10 {
		n := new(big.Int)
		_, ok := n.SetString(v.value, 10)
		if !ok {
			panic("error converting string to big.Int")
		}
		return n.Bytes()
	}
	panic("unsupported base")
}

var tests = []Test{
	{
		preimages: []ValueWithBase{
			// zero-length
			{"", 16},
		},
		hashCheck: [2]HashCheck{
			{curve: ecc.BN254,
				value: ValueWithBase{
					"20104241803663641422577121134203490505137011783614913652735802145961801733870", 10,
				}},
			{curve: ecc.BLS12_381,
				value: ValueWithBase{
					"17991912493598890696181760734961918471863781118188078948205844982816313445306", 10,
				}},
		},
	},
	{
		preimages: []ValueWithBase{
			// 32 bytes, less than modulus
			{"23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535", 16},
		},
		hashCheck: [2]HashCheck{
			{curve: ecc.BN254,
				value: ValueWithBase{
					"12886436712380113721405259596386800092738845035233065858332878701083870690753", 10,
				}},
			{curve: ecc.BLS12_381,
				value: ValueWithBase{
					"8791766422525455185980675814845076441443662947059416063736889106252015893524", 10,
				}},
		},
	},
	{
		preimages: []ValueWithBase{
			// 32 bytes, more than modulus
			{"73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000002", 16},
		},
		hashCheck: [2]HashCheck{
			{curve: ecc.BN254,
				value: ValueWithBase{
					"19565877911319815535452130675266047290072088868113536892077808700068649624391", 10,
				}},
			{curve: ecc.BLS12_381,
				value: ValueWithBase{
					"35137972692771717943992759113612269767581262500164574105059686144346651628747", 10,
				}},
		},
	},
	{
		// less than 32 bytes
		preimages: []ValueWithBase{{"deadf00d", 16}},
		hashCheck: [2]HashCheck{
			{curve: ecc.BN254,
				value: ValueWithBase{
					"1037254799353855871006189384309576393135431139055333626960622147300727796413", 10,
				}},
			{curve: ecc.BLS12_381,
				value: ValueWithBase{
					"15039173432183897369859775531867817848264266283034981501223857291379142522368", 10,
				}},
		},
	},
	{
		// 32 bytes, less than modulus | 32 bytes, less than modulus | 32 bytes, less than modulus
		preimages: []ValueWithBase{
			{"183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217", 16},
			{"23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535", 16},
			{"30644e72e131a029b85045b68181585d2833e84879b9709143e1f593ef676981", 16},
		},
		hashCheck: [2]HashCheck{
			{curve: ecc.BN254,
				value: ValueWithBase{
					"6040222623731283351958201178122781676432899642144860863024149088913741383362", 10,
				}},
			{curve: ecc.BLS12_381,
				value: ValueWithBase{
					"12964111614552580241101202600014316932811348627866250816177200046290462797607", 10,
				}},
		},
	},
	{
		// 32 bytes, less than modulus | 32 bytes, less than modulus | 32 bytes, more than modulus
		preimages: []ValueWithBase{
			{"183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217", 16},
			{"23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535", 16},
			{"73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000002", 16},
		},
		hashCheck: [2]HashCheck{
			{curve: ecc.BN254,
				value: ValueWithBase{
					"21691351735381703396517600859480938764038501053226864452091917666642352837076", 10,
				}},
			{curve: ecc.BLS12_381,
				value: ValueWithBase{
					"21773894974440411325489312534417904228129169539217646609523079291104496302656", 10,
				}},
		},
	},
	{
		// 32 bytes, less than modulus | 32 bytes, less than modulus | less than 32 bytes
		preimages: []ValueWithBase{
			{"183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217", 16},
			{"23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535", 16},
			{"abba", 16},
		},
		hashCheck: [2]HashCheck{
			{curve: ecc.BN254,
				value: ValueWithBase{
					"10501393540371963307040960561318023073151272109639330842515119353134949995409", 10,
				}},
			{curve: ecc.BLS12_381,
				value: ValueWithBase{
					"9873666029497961930790892458408217321483390383568592297687427911011295910871", 10,
				}},
		},
	},
}

type CircuitOneInput struct {
	Secret frontend.Variable
	Hash   frontend.Variable `gnark:",public"`
}

func (circuit *CircuitOneInput) Define(api frontend.API) error {
	mimc, _ := mimc.NewMiMC(api)

	mimc.Write(circuit.Secret)
	hash := mimc.Sum()
	api.Println("hash:", hash)

	api.AssertIsEqual(circuit.Hash, hash)

	return nil
}

type CircuitThreeInputs struct {
	Secret1 frontend.Variable
	Secret2 frontend.Variable
	Secret3 frontend.Variable
	Hash    frontend.Variable `gnark:",public"`
}

func (circuit *CircuitThreeInputs) Define(api frontend.API) error {
	mimc, _ := mimc.NewMiMC(api)

	mimc.Write(circuit.Secret1)
	mimc.Write(circuit.Secret2)
	mimc.Write(circuit.Secret3)

	hash := mimc.Sum()
	api.Println("hash:", hash)

	api.AssertIsEqual(circuit.Hash, hash)

	return nil
}
