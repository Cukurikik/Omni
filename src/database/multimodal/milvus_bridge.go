package multimodal

import (
	"context"
	"errors"
	"fmt"

	"github.com/milvus-io/milvus-sdk-go/v2/client"
	"github.com/milvus-io/milvus-sdk-go/v2/entity"
)

type MilvusBridge struct {
	client client.Client
}

func NewMilvusBridge(ctx context.Context, address string) (*MilvusBridge, error) {
	c, err := client.NewClient(ctx, client.Config{
		Address: address,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to Milvus: %w", err)
	}
	return &MilvusBridge{client: c}, nil
}

func (b *MilvusBridge) InsertMultimodal(ctx context.Context, collName string, ids []int64, textEmbeds [][]float32, imgEmbeds [][]float32) error {
	if len(ids) == 0 {
		return errors.New("empty ids")
	}

	idCol := entity.NewColumnInt64("id", ids)

	cols := []entity.Column{idCol}

	if len(textEmbeds) > 0 {
		textCol := entity.NewColumnFloatVector("text_embedding", 512, textEmbeds)
		cols = append(cols, textCol)
	}

	if len(imgEmbeds) > 0 {
		imgCol := entity.NewColumnFloatVector("image_embedding", 512, imgEmbeds)
		cols = append(cols, imgCol)
	}

	_, err := b.client.Insert(ctx, collName, "", cols...)
	return err
}

func (b *MilvusBridge) Close() error {
	return b.client.Close()
}
