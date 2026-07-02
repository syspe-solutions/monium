from apps.common.constants import DEVELOPMENT_REGIONS, IBGE_MUNICIPALITY
from apps.common.models import DevelopmentRegion, Municipality
from apps.common.seeds.base_seed import BaseSeed


class LocationSeed(BaseSeed):

    def run(self) -> str:
        regions_created_count = 0
        mun_created_count = 0


        for development_region in DEVELOPMENT_REGIONS: 
            region, created = DevelopmentRegion.objects.get_or_create(
                name=development_region["name"],
                acronym= development_region["acronym"]
            )
            
            if created:
                regions_created_count += 1
            
        for municipality in IBGE_MUNICIPALITY:
            try:
                region = DevelopmentRegion.objects.filter(
                        acronym=municipality.get("development_region") 
                    ).first()                
                _, created = Municipality.objects.get_or_create(
                    name=municipality['name'],
                    ibge_code=municipality['ibge_code'],
                    region=region,
                )
                
                if created:
                    mun_created_count += 1
                    
            except DevelopmentRegion.DoesNotExist:
                print(f"Erro: Região {municipality['region_slug']} não encontrada para {municipality['name']}")

        if regions_created_count or mun_created_count:
            return f"✔ Pernambuco populado: {regions_created_count} RDs e {mun_created_count} Municípios."
        return "! Dados de Pernambuco já estão atualizados."