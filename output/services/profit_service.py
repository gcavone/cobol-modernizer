import logging
from decimal import Decimal
from typing import List, Optional
from repositories.profit_repository import ProfitRepository
from services.activity_service import ActivityService
from models.profit_record import ProfitRecord


class ProfitService:
    """Service for managing profit calculations.
    
    Handles profit calculation and implements the business rule:
    PROFIT = SELLING_PRICE - COGS
    """

    def __init__(self, profit_repo: ProfitRepository,
                 activity_service: ActivityService) -> None:
        """Initialize ProfitService with repositories and services.
        
        Args:
            profit_repo: Repository for profit record data access.
            activity_service: Service for logging activities.
        """
        self.profit_repo: ProfitRepository = profit_repo
        self.activity_service: ActivityService = activity_service
        self.logger: logging.Logger = logging.getLogger(__name__)

    def calculate_profit(self, cogs: Decimal, selling_price: Decimal, 
                        admin_id: int) -> ProfitRecord:
        """Calculate and record profit.
        
        Implements business rule: PROFIT = SELLING_PRICE - COGS
        
        Args:
            cogs: Cost of goods sold (must be >= 0).
            selling_price: Selling price (must be > 0).
            admin_id: ID of admin performing the calculation.
        
        Returns:
            ProfitRecord with calculated profit.
        
        Raises:
            ValueError: If values invalid.
        """
        # Validate and convert COGS
        try:
            cogs_decimal: Decimal = Decimal(str(cogs))
        except (ValueError, TypeError):
            raise ValueError("COGS must be a valid number")

        if cogs_decimal < 0:
            raise ValueError("COGS cannot be negative")

        # Validate and convert selling price
        try:
            selling_price_decimal: Decimal = Decimal(str(selling_price))
        except (ValueError, TypeError):
            raise ValueError("Selling price must be a valid number")

        if selling_price_decimal <= 0:
            raise ValueError("Selling price must be positive")

        # Calculate profit: PROFIT = SELLING_PRICE - COGS
        profit: Decimal = selling_price_decimal - cogs_decimal

        # Create profit record
        profit_record: ProfitRecord = self.profit_repo.create(
            cogs=float(cogs_decimal),
            selling_price=float(selling_price_decimal),
            profit=float(profit)
        )

        # Log activity
        self.activity_service.log_action(
            action="PROFIT_CALCULATED",
            entity_type="PROFIT",
            entity_id=profit_record.id,
            admin_id=admin_id,
            details=f"COGS: {cogs_decimal}, Selling Price: {selling_price_decimal}, Profit: {profit}"
        )

        self.logger.info(
            f"Profit calculated: {selling_price_decimal} - {cogs_decimal} = {profit}"
        )

        return profit_record

    def get_profit_by_id(self, profit_id: int) -> ProfitRecord:
        """Retrieve a profit record by ID.
        
        Args:
            profit_id: The profit record ID.
        
        Returns:
            ProfitRecord instance.
        
        Raises:
            ValueError: If profit record not found.
        """
        profit: Optional[ProfitRecord] = self.profit_repo.get_by_id(profit_id)
        if not profit:
            raise ValueError(f"Profit record {profit_id} not found")
        return profit

    def list_all_profits(self) -> List[ProfitRecord]:
        """Retrieve all profit records.
        
        Returns:
            List of all ProfitRecord instances.
        """
        return self.profit_repo.get_all()
