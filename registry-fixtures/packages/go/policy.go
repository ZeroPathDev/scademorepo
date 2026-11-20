package policy

import "github.com/google/uuid"

func Version() string { return "1.0.0 (" + uuid.Nil.String() + ")" }
