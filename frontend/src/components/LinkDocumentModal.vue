<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
    <div class="bg-card w-full max-w-lg rounded-xl shadow-2xl border border-border overflow-hidden animate-in zoom-in-95 duration-200">
      <div class="p-6 border-b border-border flex justify-between items-center bg-muted/30">
        <h2 class="text-xl font-semibold text-foreground">
          Lier un {{ type === 'devis' ? 'rapport' : 'devis' }}
        </h2>
        <button @click="$emit('close')" class="p-2 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>
      
      <div class="p-6">
        <div v-if="loading" class="flex flex-col items-center justify-center py-12 space-y-4">
          <div class="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p class="text-muted-foreground">Chargement des documents...</p>
        </div>
        
        <div v-else-if="items.length === 0" class="flex flex-col items-center justify-center py-12 space-y-4 text-center">
          <FileQuestion class="w-16 h-16 text-muted-foreground/30" />
          <div>
            <p class="text-lg font-medium text-foreground">Aucun document disponible</p>
            <p class="text-sm text-muted-foreground">
              Vous n'avez pas d'autre {{ type === 'devis' ? 'rapport' : 'devis' }} 
              {{ clientId ? 'pour ce client' : '' }} à lier pour le moment.
            </p>
          </div>
        </div>
        
        <div v-else class="space-y-3 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
          <p class="text-sm text-muted-foreground mb-4">
            Sélectionnez le {{ type === 'devis' ? 'rapport' : 'devis' }} que vous souhaitez associer à ce document.
          </p>
          
          <div 
            v-for="item in items" 
            :key="item.id"
            @click="selectItem(item)"
            class="group p-4 rounded-lg border border-border hover:border-primary hover:bg-primary/5 cursor-pointer transition-all flex items-center justify-between"
            :class="{'border-primary bg-primary/5 ring-1 ring-primary': selectedId === item.id}"
          >
            <div class="flex items-center">
              <div class="w-10 h-10 rounded-full bg-muted flex items-center justify-center mr-4 group-hover:bg-primary/10 transition-colors">
                <FileText v-if="type === 'devis'" class="w-5 h-5 text-muted-foreground group-hover:text-primary" />
                <ClipboardList v-else class="w-5 h-5 text-muted-foreground group-hover:text-primary" />
              </div>
              <div class="flex flex-col">
                <span class="font-medium text-foreground">
                  {{ type === 'devis' ? 'Rapport' : 'Devis' }} #{{ item.id }}
                </span>
                <span class="text-xs text-muted-foreground">
                  {{ item.client?.nom || 'Client inconnu' }} - {{ formatDate(item.created_at) }}
                </span>
              </div>
            </div>
            <div v-if="selectedId === item.id" class="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
              <Check class="w-4 h-4 text-primary-foreground" />
            </div>
            <ChevronRight v-else class="w-5 h-5 text-muted-foreground group-hover:text-primary transition-transform group-hover:translate-x-1" />
          </div>
        </div>
      </div>
      
      <div class="p-6 border-t border-border bg-muted/30 flex justify-end space-x-3">
        <button 
          @click="$emit('close')"
          class="px-4 py-2 text-sm font-medium text-foreground hover:bg-muted rounded-lg transition-colors"
        >
          Annuler
        </button>
        <button 
          @click="confirmSelection"
          :disabled="!selectedId"
          class="btn-primary"
        >
          Confirmer le lien
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { X, FileText, ClipboardList, Check, ChevronRight, FileQuestion } from 'lucide-vue-next';
import { apiFetch } from '@/lib/api';

const props = defineProps<{
  isOpen: boolean;
  type: 'devis' | 'rapport';
  clientId?: number;
}>();

const emit = defineEmits(['close', 'select']);

const items = ref<any[]>([]);
const loading = ref(true);
const selectedId = ref<number | null>(null);

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

const fetchItems = async () => {
  if (!props.isOpen) return;
  
  loading.value = true;
  try {
    const endpoint = props.type === 'devis' ? '/rapports' : '/devis';
    const response = await apiFetch(endpoint);
    const data = await response.json();
    
    // Filter out already linked items and filter by client if provided
    items.value = data.filter((item: any) => {
      const isAlreadyLinked = props.type === 'devis' ? item.id_devis : item.id_rapport;
      // If we are on a Devis, we look for Rapports. item.id_client matches.
      const matchesClient = !props.clientId || item.id_client === props.clientId;
      return !isAlreadyLinked && matchesClient;
    });
  } catch (error) {
    console.error('Error fetching items:', error);
  } finally {
    loading.value = false;
  }
};

const selectItem = (item: any) => {
  selectedId.value = item.id;
};

const confirmSelection = () => {
  if (selectedId.value) {
    emit('select', selectedId.value);
    emit('close');
  }
};

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    selectedId.value = null;
    fetchItems();
  }
});
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--muted-foreground);
}
</style>
