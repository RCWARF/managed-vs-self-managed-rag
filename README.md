# Managed vs Self-Managed RAG on AWS

Benchmarking Retrieval-Augmented Generation (RAG) pipelines in cloud environments by comparing serverless (managed) architectures with self-managed deployments on EC2.

## Overview

This project supports my M.S. thesis research at the University of Washington Tacoma. It implements and evaluates two functionally equivalent RAG pipelines:

- **Serverless / Managed Pipeline** using AWS-managed services and event-driven orchestration
- **Self-Managed Pipeline** using EC2-hosted components with explicit service control

The goal is to analyze trade-offs in:

- Latency
- Throughput
- Scalability
- Reliability
- Cost

This repository is designed as both a research platform and a reproducible engineering system.

---

## Architecture

### High-Level Design

[INSERT DIAGRAM HERE]

The system is structured into three main stages:

1. **Ingestion**
   - Document loading and preprocessing
   - Chunking and embedding generation
   - Storage in vector database

2. **Retrieval**
   - Query embedding
   - Similarity search over vector store
   - Context selection

3. **Generation**
   - Prompt construction
   - LLM inference
   - Response generation

---

## Pipeline Implementations

### 1. Serverless / Managed Pipeline

- AWS Lambda for orchestration
- Managed embedding and LLM services
- Managed vector storage
- Event-driven ingestion and query workflows

**Characteristics:**
- Minimal infrastructure management
- Scales automatically
- Potential trade-offs in observability and cost transparency

---

### 2. Self-Managed EC2 Pipeline

- Services deployed on EC2 instances
- Self-hosted embedding models and vector database
- Explicit orchestration and service communication
- Containerized or service-based architecture

**Characteristics:**
- Full control over infrastructure and models
- Increased operational complexity
- Greater visibility into system behavior

---

## Repository Structure

```text
src/
  core/          # Shared RAG logic
  serverless/    # Lambda-based pipeline
  ec2/           # Self-managed services
  evaluation/    # Performance and cost measurement

infra/
  serverless/    # AWS serverless configs
  ec2/           # EC2 deployment configs

experiments/
  configs/       # Experiment definitions
  runs/          # Output data

scripts/         # Execution entry points
docs/            # Architecture and experiment documentation
results/         # Sample outputs and summaries
