from apps.common.services.cache_service import EligibilityNamespace, ProductivityNamespace


class CacheProvider:    
    @staticmethod
    def productivity_stats(agent_id: int):
        return {
            "key_args": (ProductivityNamespace, "stats", agent_id),
            "namespace": ProductivityNamespace
        }

    @staticmethod
    def client_eligibility(client_id: int):
        return {
            "key_args": (EligibilityNamespace, "check", client_id),
            "namespace": EligibilityNamespace
        }