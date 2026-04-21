// OMNI Gorgonia Engine
// =====================
// Production-grade, zero-mock computation graph engine for Go,
// inspired by gorgonia/gorgonia. Implements a native computation
// graph with automatic differentiation, tape-based gradient recording,
// and TapeMachine execution — all zero-dependency (only stdlib).
//
// Extracted Patterns:
//   - Computation graph with Node/Edge topology
//   - Automatic differentiation (reverse-mode AD, backpropagation)
//   - Tape-based gradient recording (Wengert list)
//   - TapeMachine executor (forward + backward pass)
//   - Operations: MatMul, Add, Mul, Sigmoid, ReLU, Tanh, Softmax, Log, Exp
//   - Tensor shape tracking and broadcasting
//   - Xavier/He weight initialization
//   - SGD and Adam optimizers
//   - Loss functions: MSE, CrossEntropy
//   - Node value caching for efficient backprop
//
// OMNI Layer: network (Go)

package go_core

import (
	"fmt"
	"math"
	"math/rand"
	"strings"
	"sync"
)

// ============================================================================
// 1. TENSOR — Multi-dimensional float64 array
// ============================================================================

// Tensor represents a multi-dimensional array of float64 values.
type Tensor struct {
	Data  []float64
	Shape []int
}

// NewTensor creates a new tensor with the given shape, initialized to zeros.
func NewTensor(shape ...int) *Tensor {
	size := 1
	for _, s := range shape {
		size *= s
	}
	return &Tensor{
		Data:  make([]float64, size),
		Shape: shape,
	}
}

// NewTensorFromData creates a tensor from existing data and shape.
func NewTensorFromData(data []float64, shape ...int) *Tensor {
	return &Tensor{Data: data, Shape: shape}
}

// NewTensorRand creates a tensor with random normal values.
func NewTensorRand(shape ...int) *Tensor {
	t := NewTensor(shape...)
	for i := range t.Data {
		t.Data[i] = rand.NormFloat64()
	}
	return t
}

// XavierInit creates a tensor with Xavier/Glorot initialization.
func XavierInit(fanIn, fanOut int) *Tensor {
	t := NewTensor(fanIn, fanOut)
	limit := math.Sqrt(6.0 / float64(fanIn+fanOut))
	for i := range t.Data {
		t.Data[i] = (rand.Float64()*2 - 1) * limit
	}
	return t
}

// HeInit creates a tensor with He/Kaiming initialization.
func HeInit(fanIn, fanOut int) *Tensor {
	t := NewTensor(fanIn, fanOut)
	std := math.Sqrt(2.0 / float64(fanIn))
	for i := range t.Data {
		t.Data[i] = rand.NormFloat64() * std
	}
	return t
}

// Size returns the total number of elements.
func (t *Tensor) Size() int {
	if t == nil || len(t.Data) == 0 {
		return 0
	}
	return len(t.Data)
}

// Clone creates a deep copy.
func (t *Tensor) Clone() *Tensor {
	data := make([]float64, len(t.Data))
	copy(data, t.Data)
	shape := make([]int, len(t.Shape))
	copy(shape, t.Shape)
	return &Tensor{Data: data, Shape: shape}
}

// At returns the element at row i, col j (2D tensors only).
func (t *Tensor) At(i, j int) float64 {
	if len(t.Shape) != 2 {
		return 0
	}
	return t.Data[i*t.Shape[1]+j]
}

// Set sets the element at row i, col j (2D tensors only).
func (t *Tensor) Set(i, j int, val float64) {
	if len(t.Shape) != 2 {
		return
	}
	t.Data[i*t.Shape[1]+j] = val
}

// Zeros fills the tensor with zeros.
func (t *Tensor) Zeros() {
	for i := range t.Data {
		t.Data[i] = 0
	}
}

// ============================================================================
// 2. TENSOR OPERATIONS
// ============================================================================

// MatMul performs matrix multiplication: C = A @ B
func MatMul(a, b *Tensor) (*Tensor, error) {
	if len(a.Shape) != 2 || len(b.Shape) != 2 {
		return nil, fmt.Errorf("matmul requires 2D tensors, got %v and %v", a.Shape, b.Shape)
	}
	M, K1 := a.Shape[0], a.Shape[1]
	K2, N := b.Shape[0], b.Shape[1]
	if K1 != K2 {
		return nil, fmt.Errorf("matmul shape mismatch: (%d,%d) @ (%d,%d)", M, K1, K2, N)
	}
	c := NewTensor(M, N)
	for i := 0; i < M; i++ {
		for j := 0; j < N; j++ {
			sum := 0.0
			for k := 0; k < K1; k++ {
				sum += a.Data[i*K1+k] * b.Data[k*N+j]
			}
			c.Data[i*N+j] = sum
		}
	}
	return c, nil
}

// Transpose returns the transpose of a 2D tensor.
func Transpose(a *Tensor) *Tensor {
	if len(a.Shape) != 2 {
		return a.Clone()
	}
	rows, cols := a.Shape[0], a.Shape[1]
	t := NewTensor(cols, rows)
	for i := 0; i < rows; i++ {
		for j := 0; j < cols; j++ {
			t.Data[j*rows+i] = a.Data[i*cols+j]
		}
	}
	return t
}

// Add performs element-wise addition with broadcasting.
func Add(a, b *Tensor) (*Tensor, error) {
	if len(a.Data) == len(b.Data) {
		c := NewTensor(a.Shape...)
		for i := range a.Data {
			c.Data[i] = a.Data[i] + b.Data[i]
		}
		return c, nil
	}
	// Broadcasting: b is a bias vector (1, N)
	if len(a.Shape) == 2 && len(b.Shape) == 2 && b.Shape[0] == 1 {
		c := NewTensor(a.Shape...)
		cols := a.Shape[1]
		for i := 0; i < a.Shape[0]; i++ {
			for j := 0; j < cols; j++ {
				c.Data[i*cols+j] = a.Data[i*cols+j] + b.Data[j]
			}
		}
		return c, nil
	}
	return nil, fmt.Errorf("incompatible shapes for add: %v and %v", a.Shape, b.Shape)
}

// HadamardMul performs element-wise multiplication.
func HadamardMul(a, b *Tensor) (*Tensor, error) {
	if len(a.Data) != len(b.Data) {
		return nil, fmt.Errorf("hadamard mul shape mismatch: %v vs %v", a.Shape, b.Shape)
	}
	c := NewTensor(a.Shape...)
	for i := range a.Data {
		c.Data[i] = a.Data[i] * b.Data[i]
	}
	return c, nil
}

// ScalarMul multiplies all elements by scalar.
func ScalarMul(a *Tensor, s float64) *Tensor {
	c := NewTensor(a.Shape...)
	for i := range a.Data {
		c.Data[i] = a.Data[i] * s
	}
	return c
}

// ============================================================================
// 3. ACTIVATION FUNCTIONS
// ============================================================================

func SigmoidTensor(a *Tensor) *Tensor {
	c := NewTensor(a.Shape...)
	for i, v := range a.Data {
		c.Data[i] = 1.0 / (1.0 + math.Exp(-clip(v, -500, 500)))
	}
	return c
}

func ReLUTensor(a *Tensor) *Tensor {
	c := NewTensor(a.Shape...)
	for i, v := range a.Data {
		if v > 0 {
			c.Data[i] = v
		}
	}
	return c
}

func TanhTensor(a *Tensor) *Tensor {
	c := NewTensor(a.Shape...)
	for i, v := range a.Data {
		c.Data[i] = math.Tanh(v)
	}
	return c
}

func SoftmaxTensor(a *Tensor) *Tensor {
	if len(a.Shape) != 2 {
		return a.Clone()
	}
	rows, cols := a.Shape[0], a.Shape[1]
	c := NewTensor(rows, cols)
	for i := 0; i < rows; i++ {
		maxVal := math.Inf(-1)
		for j := 0; j < cols; j++ {
			if a.Data[i*cols+j] > maxVal {
				maxVal = a.Data[i*cols+j]
			}
		}
		sumExp := 0.0
		for j := 0; j < cols; j++ {
			c.Data[i*cols+j] = math.Exp(a.Data[i*cols+j] - maxVal)
			sumExp += c.Data[i*cols+j]
		}
		for j := 0; j < cols; j++ {
			c.Data[i*cols+j] /= sumExp
		}
	}
	return c
}

func ExpTensor(a *Tensor) *Tensor {
	c := NewTensor(a.Shape...)
	for i, v := range a.Data {
		c.Data[i] = math.Exp(clip(v, -500, 500))
	}
	return c
}

func LogTensor(a *Tensor) *Tensor {
	c := NewTensor(a.Shape...)
	for i, v := range a.Data {
		if v <= 0 {
			v = 1e-7
		}
		c.Data[i] = math.Log(v)
	}
	return c
}

func clip(v, lo, hi float64) float64 {
	if v < lo {
		return lo
	}
	if v > hi {
		return hi
	}
	return v
}

// ============================================================================
// 4. COMPUTATION GRAPH — Node & Edge
// ============================================================================

// OpType defines the operation type for a graph node.
type OpType int

const (
	OpInput OpType = iota
	OpMatMul
	OpAdd
	OpMul
	OpSigmoid
	OpReLU
	OpTanh
	OpSoftmax
	OpExp
	OpLog
	OpMSELoss
	OpCrossEntropyLoss
)

func (op OpType) String() string {
	names := []string{
		"Input", "MatMul", "Add", "Mul", "Sigmoid", "ReLU",
		"Tanh", "Softmax", "Exp", "Log", "MSELoss", "CrossEntropyLoss",
	}
	if int(op) < len(names) {
		return names[op]
	}
	return "Unknown"
}

// Node represents a computation node in the graph.
type Node struct {
	ID       int
	Name     string
	Op       OpType
	Value    *Tensor
	Grad     *Tensor
	Inputs   []*Node
	IsParam  bool // Learnable parameter
}

// ExprGraph is the computation graph container.
type ExprGraph struct {
	mu    sync.Mutex
	nodes []*Node
	nextID int
}

// NewGraph creates a new computation graph.
func NewGraph() *ExprGraph {
	return &ExprGraph{nodes: make([]*Node, 0)}
}

// NewScalar creates a scalar (1x1) input node.
func (g *ExprGraph) NewScalar(value float64, name string) *Node {
	return g.addNode(name, OpInput, NewTensorFromData([]float64{value}, 1, 1), nil, false)
}

// NewMatrix creates a matrix input node.
func (g *ExprGraph) NewMatrix(t *Tensor, name string) *Node {
	return g.addNode(name, OpInput, t, nil, false)
}

// NewParam creates a learnable parameter node.
func (g *ExprGraph) NewParam(t *Tensor, name string) *Node {
	return g.addNode(name, OpInput, t, nil, true)
}

func (g *ExprGraph) addNode(name string, op OpType, value *Tensor, inputs []*Node, isParam bool) *Node {
	g.mu.Lock()
	defer g.mu.Unlock()
	n := &Node{
		ID:      g.nextID,
		Name:    name,
		Op:      op,
		Value:   value,
		Inputs:  inputs,
		IsParam: isParam,
	}
	g.nextID++
	g.nodes = append(g.nodes, n)
	return n
}

// Nodes returns all nodes in the graph.
func (g *ExprGraph) Nodes() []*Node {
	return g.nodes
}

// Params returns all learnable parameter nodes.
func (g *ExprGraph) Params() []*Node {
	var params []*Node
	for _, n := range g.nodes {
		if n.IsParam {
			params = append(params, n)
		}
	}
	return params
}

// ============================================================================
// 5. GRAPH OPERATIONS (build computation graph)
// ============================================================================

// MatMulOp creates a MatMul node: C = A @ B
func MatMulOp(g *ExprGraph, a, b *Node) *Node {
	return g.addNode("matmul", OpMatMul, nil, []*Node{a, b}, false)
}

// AddOp creates an Add node: C = A + B
func AddOp(g *ExprGraph, a, b *Node) *Node {
	return g.addNode("add", OpAdd, nil, []*Node{a, b}, false)
}

// MulOp creates element-wise multiply node.
func MulOp(g *ExprGraph, a, b *Node) *Node {
	return g.addNode("mul", OpMul, nil, []*Node{a, b}, false)
}

// SigmoidOp creates a Sigmoid activation node.
func SigmoidOp(g *ExprGraph, a *Node) *Node {
	return g.addNode("sigmoid", OpSigmoid, nil, []*Node{a}, false)
}

// ReLUOp creates a ReLU activation node.
func ReLUOp(g *ExprGraph, a *Node) *Node {
	return g.addNode("relu", OpReLU, nil, []*Node{a}, false)
}

// TanhOp creates a Tanh activation node.
func TanhOp(g *ExprGraph, a *Node) *Node {
	return g.addNode("tanh", OpTanh, nil, []*Node{a}, false)
}

// SoftmaxOp creates a Softmax node.
func SoftmaxOp(g *ExprGraph, a *Node) *Node {
	return g.addNode("softmax", OpSoftmax, nil, []*Node{a}, false)
}

// MSELossOp creates Mean Squared Error loss node.
func MSELossOp(g *ExprGraph, pred, target *Node) *Node {
	return g.addNode("mse_loss", OpMSELoss, nil, []*Node{pred, target}, false)
}

// CrossEntropyLossOp creates Cross-Entropy loss node.
func CrossEntropyLossOp(g *ExprGraph, pred, target *Node) *Node {
	return g.addNode("ce_loss", OpCrossEntropyLoss, nil, []*Node{pred, target}, false)
}

// ============================================================================
// 6. TAPE MACHINE — Forward & Backward Execution
// ============================================================================

// TapeEntry records a single operation for gradient computation.
type TapeEntry struct {
	Node    *Node
	Inputs  []*Node
	Op      OpType
}

// TapeMachine executes computation graph and records tape for backprop.
type TapeMachine struct {
	graph *ExprGraph
	tape  []TapeEntry
}

// NewTapeMachine creates a TapeMachine for the given graph.
func NewTapeMachine(g *ExprGraph) *TapeMachine {
	return &TapeMachine{graph: g}
}

// Forward executes all nodes in topological order, recording the tape.
func (tm *TapeMachine) Forward() error {
	tm.tape = make([]TapeEntry, 0, len(tm.graph.nodes))

	for _, node := range tm.graph.nodes {
		if node.Op == OpInput {
			// Input nodes already have values
			continue
		}
		var err error
		switch node.Op {
		case OpMatMul:
			node.Value, err = MatMul(node.Inputs[0].Value, node.Inputs[1].Value)
		case OpAdd:
			node.Value, err = Add(node.Inputs[0].Value, node.Inputs[1].Value)
		case OpMul:
			node.Value, err = HadamardMul(node.Inputs[0].Value, node.Inputs[1].Value)
		case OpSigmoid:
			node.Value = SigmoidTensor(node.Inputs[0].Value)
		case OpReLU:
			node.Value = ReLUTensor(node.Inputs[0].Value)
		case OpTanh:
			node.Value = TanhTensor(node.Inputs[0].Value)
		case OpSoftmax:
			node.Value = SoftmaxTensor(node.Inputs[0].Value)
		case OpExp:
			node.Value = ExpTensor(node.Inputs[0].Value)
		case OpLog:
			node.Value = LogTensor(node.Inputs[0].Value)
		case OpMSELoss:
			node.Value = mseForward(node.Inputs[0].Value, node.Inputs[1].Value)
		case OpCrossEntropyLoss:
			node.Value = crossEntropyForward(node.Inputs[0].Value, node.Inputs[1].Value)
		default:
			err = fmt.Errorf("unknown op: %v", node.Op)
		}
		if err != nil {
			return fmt.Errorf("forward error at node %d (%s): %w", node.ID, node.Name, err)
		}
		tm.tape = append(tm.tape, TapeEntry{Node: node, Inputs: node.Inputs, Op: node.Op})
	}
	return nil
}

// Backward performs reverse-mode automatic differentiation.
func (tm *TapeMachine) Backward(lossNode *Node) error {
	// Initialize loss gradient to 1.0
	lossNode.Grad = NewTensor(lossNode.Value.Shape...)
	for i := range lossNode.Grad.Data {
		lossNode.Grad.Data[i] = 1.0
	}

	// Reverse tape
	for i := len(tm.tape) - 1; i >= 0; i-- {
		entry := tm.tape[i]
		node := entry.Node
		if node.Grad == nil {
			continue
		}

		switch entry.Op {
		case OpMatMul:
			a, b := entry.Inputs[0], entry.Inputs[1]
			// dA = dOut @ B^T
			bT := Transpose(b.Value)
			dA, _ := MatMul(node.Grad, bT)
			accumulateGrad(a, dA)
			// dB = A^T @ dOut
			aT := Transpose(a.Value)
			dB, _ := MatMul(aT, node.Grad)
			accumulateGrad(b, dB)

		case OpAdd:
			a, b := entry.Inputs[0], entry.Inputs[1]
			accumulateGrad(a, node.Grad)
			// Handle broadcast: sum along batch dim for bias
			if len(b.Value.Shape) == 2 && b.Value.Shape[0] == 1 && len(a.Value.Shape) == 2 {
				bGrad := NewTensor(1, b.Value.Shape[1])
				cols := b.Value.Shape[1]
				rows := a.Value.Shape[0]
				for j := 0; j < cols; j++ {
					sum := 0.0
					for r := 0; r < rows; r++ {
						sum += node.Grad.Data[r*cols+j]
					}
					bGrad.Data[j] = sum
				}
				accumulateGrad(b, bGrad)
			} else {
				accumulateGrad(b, node.Grad)
			}

		case OpMul:
			a, b := entry.Inputs[0], entry.Inputs[1]
			dA, _ := HadamardMul(node.Grad, b.Value)
			accumulateGrad(a, dA)
			dB, _ := HadamardMul(node.Grad, a.Value)
			accumulateGrad(b, dB)

		case OpSigmoid:
			a := entry.Inputs[0]
			// dsigmoid = sigmoid * (1 - sigmoid)
			sig := node.Value
			dSig := NewTensor(sig.Shape...)
			for j := range sig.Data {
				dSig.Data[j] = node.Grad.Data[j] * sig.Data[j] * (1.0 - sig.Data[j])
			}
			accumulateGrad(a, dSig)

		case OpReLU:
			a := entry.Inputs[0]
			dRelu := NewTensor(a.Value.Shape...)
			for j := range a.Value.Data {
				if a.Value.Data[j] > 0 {
					dRelu.Data[j] = node.Grad.Data[j]
				}
			}
			accumulateGrad(a, dRelu)

		case OpTanh:
			a := entry.Inputs[0]
			dTanh := NewTensor(node.Value.Shape...)
			for j := range node.Value.Data {
				dTanh.Data[j] = node.Grad.Data[j] * (1.0 - node.Value.Data[j]*node.Value.Data[j])
			}
			accumulateGrad(a, dTanh)

		case OpSoftmax:
			a := entry.Inputs[0]
			// Simplified: pass gradient through (used with CE loss)
			accumulateGrad(a, node.Grad)

		case OpMSELoss:
			pred, target := entry.Inputs[0], entry.Inputs[1]
			n := float64(pred.Value.Size())
			dPred := NewTensor(pred.Value.Shape...)
			for j := range pred.Value.Data {
				dPred.Data[j] = 2.0 * (pred.Value.Data[j] - target.Value.Data[j]) / n
			}
			accumulateGrad(pred, dPred)

		case OpCrossEntropyLoss:
			pred, target := entry.Inputs[0], entry.Inputs[1]
			n := float64(pred.Value.Shape[0])
			dPred := NewTensor(pred.Value.Shape...)
			for j := range pred.Value.Data {
				dPred.Data[j] = (pred.Value.Data[j] - target.Value.Data[j]) / n
			}
			accumulateGrad(pred, dPred)
		}
	}
	return nil
}

// Reset clears all computed values and gradients (except parameter values).
func (tm *TapeMachine) Reset() {
	for _, n := range tm.graph.nodes {
		n.Grad = nil
		if !n.IsParam && n.Op != OpInput {
			n.Value = nil
		}
	}
	tm.tape = nil
}

func accumulateGrad(node *Node, grad *Tensor) {
	if node.Grad == nil {
		node.Grad = grad.Clone()
	} else {
		for i := range node.Grad.Data {
			if i < len(grad.Data) {
				node.Grad.Data[i] += grad.Data[i]
			}
		}
	}
}

// ============================================================================
// 7. LOSS FUNCTIONS
// ============================================================================

func mseForward(pred, target *Tensor) *Tensor {
	sum := 0.0
	for i := range pred.Data {
		diff := pred.Data[i] - target.Data[i]
		sum += diff * diff
	}
	mse := sum / float64(len(pred.Data))
	return NewTensorFromData([]float64{mse}, 1, 1)
}

func crossEntropyForward(pred, target *Tensor) *Tensor {
	// pred is softmax output, target is one-hot
	n := float64(pred.Shape[0])
	sum := 0.0
	for i := range pred.Data {
		p := pred.Data[i]
		if p < 1e-7 {
			p = 1e-7
		}
		sum -= target.Data[i] * math.Log(p)
	}
	return NewTensorFromData([]float64{sum / n}, 1, 1)
}

// ============================================================================
// 8. OPTIMIZERS — SGD & Adam
// ============================================================================

// GorgoniaSGD is a stochastic gradient descent optimizer.
type GorgoniaSGD struct {
	LR       float64
	Momentum float64
	velocity map[int]*Tensor
}

// NewSGD creates a new SGD optimizer.
func NewSGD(lr, momentum float64) *GorgoniaSGD {
	return &GorgoniaSGD{
		LR: lr, Momentum: momentum,
		velocity: make(map[int]*Tensor),
	}
}

// Step applies gradients to all parameter nodes.
func (o *GorgoniaSGD) Step(params []*Node) {
	for _, p := range params {
		if p.Grad == nil {
			continue
		}
		if _, ok := o.velocity[p.ID]; !ok {
			o.velocity[p.ID] = NewTensor(p.Value.Shape...)
		}
		v := o.velocity[p.ID]
		for i := range p.Value.Data {
			v.Data[i] = o.Momentum*v.Data[i] - o.LR*p.Grad.Data[i]
			p.Value.Data[i] += v.Data[i]
		}
	}
}

// GorgoniaAdam is an Adam optimizer.
type GorgoniaAdam struct {
	LR    float64
	Beta1 float64
	Beta2 float64
	Eps   float64
	T     int
	m     map[int]*Tensor
	v     map[int]*Tensor
}

// NewAdam creates a new Adam optimizer.
func NewAdam(lr float64) *GorgoniaAdam {
	return &GorgoniaAdam{
		LR: lr, Beta1: 0.9, Beta2: 0.999, Eps: 1e-8,
		m: make(map[int]*Tensor),
		v: make(map[int]*Tensor),
	}
}

// Step applies Adam update to all parameter nodes.
func (o *GorgoniaAdam) Step(params []*Node) {
	o.T++
	for _, p := range params {
		if p.Grad == nil {
			continue
		}
		if _, ok := o.m[p.ID]; !ok {
			o.m[p.ID] = NewTensor(p.Value.Shape...)
			o.v[p.ID] = NewTensor(p.Value.Shape...)
		}
		m := o.m[p.ID]
		v := o.v[p.ID]
		for i := range p.Value.Data {
			g := p.Grad.Data[i]
			m.Data[i] = o.Beta1*m.Data[i] + (1-o.Beta1)*g
			v.Data[i] = o.Beta2*v.Data[i] + (1-o.Beta2)*g*g
			mHat := m.Data[i] / (1 - math.Pow(o.Beta1, float64(o.T)))
			vHat := v.Data[i] / (1 - math.Pow(o.Beta2, float64(o.T)))
			p.Value.Data[i] -= o.LR * mHat / (math.Sqrt(vHat) + o.Eps)
		}
	}
}

// ============================================================================
// 9. OMNI ENGINE — Production Interface
// ============================================================================

// OmniGorgoniaEngine is the production interface for the Gorgonia-inspired
// computation graph engine.
type OmniGorgoniaEngine struct {
	graphs map[string]*ExprGraph
	mu     sync.RWMutex
}

// NewOmniGorgoniaEngine creates a new Gorgonia engine instance.
func NewOmniGorgoniaEngine() *OmniGorgoniaEngine {
	return &OmniGorgoniaEngine{
		graphs: make(map[string]*ExprGraph),
	}
}

// CreateGraph creates a new named computation graph.
func (e *OmniGorgoniaEngine) CreateGraph(name string) *ExprGraph {
	e.mu.Lock()
	defer e.mu.Unlock()
	g := NewGraph()
	e.graphs[name] = g
	return g
}

// GetGraph retrieves a named graph.
func (e *OmniGorgoniaEngine) GetGraph(name string) (*ExprGraph, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	g, ok := e.graphs[name]
	if !ok {
		return nil, fmt.Errorf("graph '%s' not found", name)
	}
	return g, nil
}

// TrainStep performs one forward-backward-update cycle.
func (e *OmniGorgoniaEngine) TrainStep(
	g *ExprGraph,
	lossNode *Node,
	optimizer interface{ Step([]*Node) },
) (float64, error) {
	tm := NewTapeMachine(g)

	// Forward
	if err := tm.Forward(); err != nil {
		return 0, fmt.Errorf("forward pass error: %w", err)
	}

	lossVal := 0.0
	if lossNode.Value != nil && len(lossNode.Value.Data) > 0 {
		lossVal = lossNode.Value.Data[0]
	}

	// Backward
	if err := tm.Backward(lossNode); err != nil {
		return lossVal, fmt.Errorf("backward pass error: %w", err)
	}

	// Update parameters
	optimizer.Step(g.Params())

	// Clear gradients for next iteration
	for _, n := range g.Nodes() {
		n.Grad = nil
		if !n.IsParam && n.Op != OpInput {
			n.Value = nil
		}
	}

	return lossVal, nil
}

// BuildMLP constructs a multi-layer perceptron in the graph.
func (e *OmniGorgoniaEngine) BuildMLP(
	g *ExprGraph,
	inputNode *Node,
	hiddenSizes []int,
	outputSize int,
	activation string,
) *Node {
	current := inputNode
	inputDim := inputNode.Value.Shape[1]

	for i, hSize := range hiddenSizes {
		W := g.NewParam(HeInit(inputDim, hSize), fmt.Sprintf("W%d", i))
		b := g.NewParam(NewTensor(1, hSize), fmt.Sprintf("b%d", i))
		z := MatMulOp(g, current, W)
		z = AddOp(g, z, b)

		switch strings.ToLower(activation) {
		case "relu":
			current = ReLUOp(g, z)
		case "sigmoid":
			current = SigmoidOp(g, z)
		case "tanh":
			current = TanhOp(g, z)
		default:
			current = ReLUOp(g, z)
		}
		inputDim = hSize
	}

	// Output layer
	Wout := g.NewParam(XavierInit(inputDim, outputSize), "W_out")
	bout := g.NewParam(NewTensor(1, outputSize), "b_out")
	z := MatMulOp(g, current, Wout)
	current = AddOp(g, z, bout)

	return current
}

// Diagnostics returns engine status information.
func (e *OmniGorgoniaEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	graphNames := make([]string, 0, len(e.graphs))
	for name := range e.graphs {
		graphNames = append(graphNames, name)
	}

	return map[string]interface{}{
		"engine_id":    "omni-gorgonia",
		"version":      "1.0.0",
		"graphs":       graphNames,
		"total_graphs": len(e.graphs),
		"status":       "operational",
	}
}
