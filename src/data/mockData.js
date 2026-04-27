export const mockExplorerData = {
  clusters: [
    {
      id: "cluster0",
      name: "Cluster0",
      provider: "GCP",
      region: "us-central1",
      databases: [
        {
          id: "twitter_project",
          name: "twitter_project",
          collections: [
            {
              id: "tweets",
              name: "tweets",
              documentCount: 62000
            }
          ]
        }
      ]
    }
  ],
  collections: {
    tweets: {
      documents: [
        {
          _id: "t1",
          username: "alice_dev",
          text: "Hello CS498! Building our explorer demo.",
          likes: 12,
          language: "en",
          createdAt: "2026-04-10T10:24:00.000Z"
        },
        {
          _id: "t2",
          username: "data_fan",
          text: "Mongo-style schema tab looks great.",
          likes: 30,
          language: "en",
          createdAt: "2026-04-11T08:12:00.000Z"
        },
        {
          _id: "t3",
          username: "joey",
          text: "Frontend first, backend later. Works well.",
          likes: 22,
          language: "en",
          createdAt: "2026-04-12T14:55:00.000Z"
        },
        {
          _id: "t4",
          username: "ml_student",
          text: "Need one clean demo before final submission.",
          likes: 7,
          language: "en",
          createdAt: "2026-04-12T21:03:00.000Z"
        },
        {
          _id: "t5",
          username: "cloud_ops",
          text: "GCP setup done, now wiring API.",
          likes: 15,
          language: "en",
          createdAt: "2026-04-13T05:48:00.000Z"
        }
      ],
      schema: [
        { fieldPath: "_id", types: ["string"], presenceRatio: 1 },
        { fieldPath: "username", types: ["string"], presenceRatio: 1 },
        { fieldPath: "text", types: ["string"], presenceRatio: 1 },
        { fieldPath: "likes", types: ["number"], presenceRatio: 1 },
        { fieldPath: "language", types: ["string"], presenceRatio: 1 },
        { fieldPath: "createdAt", types: ["string"], presenceRatio: 1 }
      ],
      indexes: [
        {
          name: "_id_",
          keys: { _id: 1 },
          unique: true,
          sparse: false,
          ttl: null
        },
        {
          name: "createdAt_-1",
          keys: { createdAt: -1 },
          unique: false,
          sparse: false,
          ttl: null
        }
      ],
      validation: {
        type: "jsonSchema",
        rawRule: {
          bsonType: "object",
          required: ["username", "text", "createdAt"],
          properties: {
            username: { bsonType: "string" },
            text: { bsonType: "string" },
            likes: { bsonType: "int" }
          }
        },
        lastUpdated: "2026-04-15T00:00:00.000Z"
      }
    }
  }
};