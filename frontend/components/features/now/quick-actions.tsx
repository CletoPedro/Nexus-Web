"use client";

import { Archive, BrainCircuit, CheckSquare, FileText, Plus } from "lucide-react";
import { useState } from "react";

import { DocumentForm } from "@/components/features/documents/document-form";
import { InventoryForm } from "@/components/features/inventory/inventory-form";
import { MemoryForm } from "@/components/features/memory/memory-form";
import { TaskForm } from "@/components/features/tasks/task-form";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { documentApi } from "@/lib/api/documents";
import { inventoryApi } from "@/lib/api/inventory";
import { memoryApi } from "@/lib/api/memory";
import { taskApi } from "@/lib/api/tasks";
import type { Document } from "@/types/document";

type ActionType = "memory" | "task" | "document" | "inventory" | null;

const ACTIONS: { type: Exclude<ActionType, null>; label: string; icon: typeof Plus }[] = [
  { type: "memory", label: "Memory", icon: BrainCircuit },
  { type: "task", label: "Task", icon: CheckSquare },
  { type: "document", label: "Document", icon: FileText },
  { type: "inventory", label: "Inventory", icon: Archive },
];

export function QuickActions({ onCreated }: { onCreated: () => void }) {
  const [active, setActive] = useState<ActionType>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);

  async function open(type: Exclude<ActionType, null>) {
    if (type === "inventory") {
      documentApi.list().then(setDocuments).catch(() => setDocuments([]));
    }
    setActive(type);
  }

  function close() {
    setActive(null);
  }

  async function handleCreated(createFn: () => Promise<unknown>) {
    setIsSubmitting(true);
    try {
      await createFn();
      close();
      onCreated();
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {ACTIONS.map(({ type, label, icon: Icon }) => (
          <Button key={type} variant="outline" size="sm" onClick={() => open(type)}>
            <Plus className="size-3.5" />
            <Icon className="size-3.5" />
            {label}
          </Button>
        ))}
      </div>

      <Modal open={active === "memory"} onClose={close} title="New memory">
        <MemoryForm
          submitLabel="Create memory"
          isSubmitting={isSubmitting}
          onCancel={close}
          onSubmit={(values) => handleCreated(() => memoryApi.create(values))}
        />
      </Modal>

      <Modal open={active === "task"} onClose={close} title="New task">
        <TaskForm
          submitLabel="Create task"
          isSubmitting={isSubmitting}
          onCancel={close}
          onSubmit={(values) => handleCreated(() => taskApi.create(values))}
        />
      </Modal>

      <Modal open={active === "document"} onClose={close} title="New document">
        <DocumentForm
          submitLabel="Create document"
          isSubmitting={isSubmitting}
          onCancel={close}
          onSubmit={(values) => handleCreated(() => documentApi.create(values))}
        />
      </Modal>

      <Modal open={active === "inventory"} onClose={close} title="New inventory item">
        <InventoryForm
          documents={documents}
          submitLabel="Create item"
          isSubmitting={isSubmitting}
          onCancel={close}
          onSubmit={(values) => handleCreated(() => inventoryApi.create(values))}
        />
      </Modal>
    </>
  );
}
