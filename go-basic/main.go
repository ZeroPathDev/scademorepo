package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"

	"golang.org/x/crypto/ssh"
	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
)

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("/api/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"status":"ok"}`)
	})

	mux.HandleFunc("/api/deploy", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}

		host := r.FormValue("host")
		user := r.FormValue("user")
		keyPath := r.FormValue("key_path")

		if host == "" || user == "" {
			http.Error(w, "host and user required", http.StatusBadRequest)
			return
		}

		err := executeRemoteCommand(host, user, keyPath, "systemctl restart app")
		if err != nil {
			http.Error(w, fmt.Sprintf("deploy failed: %v", err), http.StatusInternalServerError)
			return
		}

		fmt.Fprintf(w, `{"status":"deployed","host":"%s"}`, host)
	})

	mux.HandleFunc("/api/proxy", func(w http.ResponseWriter, r *http.Request) {
		target := r.URL.Query().Get("url")
		if target == "" {
			http.Error(w, "url param required", http.StatusBadRequest)
			return
		}

		resp, err := http.Get(target)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadGateway)
			return
		}
		defer resp.Body.Close()

		w.Header().Set("Content-Type", resp.Header.Get("Content-Type"))
		w.WriteHeader(resp.StatusCode)
		io.Copy(w, resp.Body)
	})

	h2s := &http2.Server{}
	handler := h2c.NewHandler(mux, h2s)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Listening on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, handler))
}

func executeRemoteCommand(host, user, keyPath, command string) error {
	if keyPath == "" {
		keyPath = os.Getenv("HOME") + "/.ssh/id_rsa"
	}

	keyData, err := os.ReadFile(keyPath)
	if err != nil {
		return fmt.Errorf("read key: %w", err)
	}

	signer, err := ssh.ParsePrivateKey(keyData)
	if err != nil {
		return fmt.Errorf("parse key: %w", err)
	}

	config := &ssh.ClientConfig{
		User: user,
		Auth: []ssh.AuthMethod{
			ssh.PublicKeys(signer),
		},
		HostKeyCallback: ssh.InsecureIgnoreHostKey(),
	}

	client, err := ssh.Dial("tcp", host+":22", config)
	if err != nil {
		return fmt.Errorf("dial: %w", err)
	}
	defer client.Close()

	session, err := client.NewSession()
	if err != nil {
		return fmt.Errorf("session: %w", err)
	}
	defer session.Close()

	output, err := session.CombinedOutput(command)
	if err != nil {
		return fmt.Errorf("exec: %w: %s", err, string(output))
	}

	log.Printf("Remote output from %s: %s", host, string(output))
	return nil
}
