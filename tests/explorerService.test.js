import test from "node:test";
import assert from "node:assert/strict";
import { MockExplorerService } from "../src/services/explorerService.js";

test("getClusters returns at least one cluster", async () => {
  const service = new MockExplorerService();
  const clusters = await service.getClusters();

  assert.ok(Array.isArray(clusters));
  assert.ok(clusters.length >= 1);
  assert.equal(clusters[0].name, "Cluster0");
});

test("getDocuments supports text filtering", async () => {
  const service = new MockExplorerService();
  const result = await service.getDocuments({
    collectionId: "tweets",
    query: "backend",
    page: 1,
    limit: 10
  });

  assert.equal(result.meta.total, 1);
  assert.match(result.items[0].text.toLowerCase(), /backend/);
});

test("getDocuments paginates consistently", async () => {
  const service = new MockExplorerService();

  const page1 = await service.getDocuments({
    collectionId: "tweets",
    page: 1,
    limit: 2
  });

  const page2 = await service.getDocuments({
    collectionId: "tweets",
    page: 2,
    limit: 2
  });

  assert.equal(page1.items.length, 2);
  assert.equal(page2.items.length, 2);
  assert.notEqual(page1.items[0]._id, page2.items[0]._id);
});