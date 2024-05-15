package main

import (
	"github.com/consensys/gnark/frontend"
	"github.com/consensys/gnark/std/hash/mimc"
)

type CircuitOneInput struct {
	Secret frontend.Variable
	Hash   frontend.Variable `gnark:",public"`
}

func (circuit *Circuit) Define(api frontend.API) error {
	mimc, _ := mimc.NewMiMC(api)

	mimc.Write(circuit.Secret)
	hash := mimc.Sum()
	api.Println(hash)
	// ensure hashes match
	api.AssertIsEqual(circuit.Hash, hash)

	return nil
}

type CircuitThreeInputs struct {
	Secret1 frontend.Variable
	Secret2 frontend.Variable
	Secret3 frontend.Variable
	Hash    frontend.Variable `gnark:",public"`
}

func (circuit *Circuit) Define(api frontend.API) error {
	mimc, _ := mimc.NewMiMC(api)

	mimc.Write(circuit.Secret1)
	mimc.Write(circuit.Secret2)
	mimc.Write(circuit.Secret3)

	hash := mimc.Sum()
	api.Println(hash)
	// ensure hashes match
	api.AssertIsEqual(circuit.Hash, hash)

	return nil
}
