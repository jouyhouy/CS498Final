import { mockExplorerData } from "../data/mockData.js";

const DEFAULT_PAGE_SIZE = 3;

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class MockExplorerService {
  constructor() {
    this.apiBase = import.meta.env?.VITE_API_BASE ?? "http://127.0.0.1:5001";
  }

  async request(path, options = {}) {
    const response = await fetch(`${this.apiBase}${path}`, {
      headers: {
        "Content-Type": "application/json"
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getClusters() {
    await delay(120);
    return mockExplorerData.clusters;
  }

  async listCollections() {
    try {
      return await this.request("/api/collections");
    } catch {
      const clusters = await this.getClusters();
      return clusters.flatMap((cluster) =>
        cluster.databases.flatMap((database) =>
          database.collections.map((collection) => ({
            name: collection.name,
            count: collection.documentCount,
            sampleDoc: mockExplorerData.collections[collection.id]?.documents?.[0] ?? null
          }))
        )
      );
    }
  }

  async runPredefinedQuery({ queryId, params = {} }) {
    try {
      return await this.request("/api/queries/run", {
        method: "POST",
        body: JSON.stringify({ queryId, params })
      });
    } catch {
      return this.runMockQuery({ queryId, params });
    }
  }

  async runMockQuery({ queryId, params = {} }) {
    await delay(120);
    if (queryId === "top-country") {
      return {
        rows: [{ country: "USA", tweet_count: 4821 }],
        count: 1,
        executionMs: 1,
        source: "mock"
      };
    }

    if (queryId === "most-active-user") {
      return {
        rows: [
          {
            user_id: 12345,
            user_name: "Black Lucifer",
            screen_name: "blcklcfr",
            tweet_count: 302
          }
        ],
        count: 1,
        executionMs: 1,
        source: "mock"
      };
    }

    const limit = Number(params.limit ?? 10);
    return {
      rows: [
        { hashtag: "mongodb", tweet_count: 95 },
        { hashtag: "cs498", tweet_count: 72 },
        { hashtag: "datascience", tweet_count: 51 },
        { hashtag: "gcp", tweet_count: 41 },
        { hashtag: "nosql", tweet_count: 36 }
      ].slice(0, Math.max(1, Math.min(limit, 100))),
      count: Math.max(1, Math.min(limit, 5)),
      executionMs: 2,
      source: "mock"
    };
  }

  async getCollection(collectionId) {
    await delay(80);
    const collection = mockExplorerData.collections[collectionId];
    if (!collection) {
      throw new Error(`Collection not found: ${collectionId}`);
    }
    return collection;
  }

  async getDocuments({ collectionId, query = "", page = 1, limit = DEFAULT_PAGE_SIZE }) {
    const collection = await this.getCollection(collectionId);
    const normalizedQuery = query.trim().toLowerCase();

    const filtered = normalizedQuery
      ? collection.documents.filter((doc) =>
          Object.values(doc).some((value) => String(value).toLowerCase().includes(normalizedQuery))
        )
      : collection.documents;

    const start = (page - 1) * limit;
    const items = filtered.slice(start, start + limit);

    return {
      items,
      meta: {
        page,
        limit,
        total: filtered.length,
        totalPages: Math.max(1, Math.ceil(filtered.length / limit))
      }
    };
  }

  async getSchema(collectionId) {
    const collection = await this.getCollection(collectionId);
    return collection.schema;
  }

  async getIndexes(collectionId) {
    const collection = await this.getCollection(collectionId);
    return collection.indexes;
  }

  async getValidation(collectionId) {
    const collection = await this.getCollection(collectionId);
    return collection.validation;
  }
}

export const explorerService = new MockExplorerService();