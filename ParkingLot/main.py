# Database Schema Design
# 1.1 Tables and Explanation
# The database schema consists of tables for ParkingLot, Floor, ParkingSlot, 
# Vehicle, and Ticket. Each table serves a specific purpose to manage and 
# track vehicles in the parking lot.

# ParkingLot Table
# sql
# Copy code
# CREATE TABLE ParkingLot (
#     parking_lot_id VARCHAR(10) PRIMARY KEY,
#     total_floors INT NOT NULL
# );
# Explanation: This table stores the unique ID and number of floors for a parking lot. 
# The parking_lot_id is the primary key since each parking lot has a unique ID, 
# essential for generating unique ticket IDs.

# Floor Table
# sql
# Copy code
# CREATE TABLE Floor (
#     floor_id INT AUTO_INCREMENT PRIMARY KEY,
#     parking_lot_id VARCHAR(10),
#     slot_count INT NOT NULL,
#     FOREIGN KEY (parking_lot_id) REFERENCES ParkingLot(parking_lot_id)
# );
# Explanation: The Floor table captures each floor within a parking lot, 
# along with the number of slots available on each floor. 
# Each floor is linked to a parking lot, 
# hence the foreign key constraint referencing ParkingLot.

# ParkingSlot Table
# sql
# Copy code
# CREATE TABLE ParkingSlot (
#     slot_id INT AUTO_INCREMENT PRIMARY KEY,
#     floor_id INT,
#     slot_type ENUM('CAR', 'BIKE', 'TRUCK') NOT NULL,
#     is_occupied BOOLEAN DEFAULT FALSE,
#     FOREIGN KEY (floor_id) REFERENCES Floor(floor_id)
# );
# Explanation: Each slot on each floor is stored in this table. 
# The slot_type field ensures only specific vehicles are parked in the matching slot, 
# and is_occupied helps track availability. Foreign key references link each slot to its floor.

# Vehicle Table
# sql
# Copy code
# CREATE TABLE Vehicle (
#     reg_no VARCHAR(15) PRIMARY KEY,
#     color VARCHAR(10),
#     vehicle_type ENUM('CAR', 'BIKE', 'TRUCK') NOT NULL
# );
# Explanation: This table stores vehicle details such as registration number, 
# color, and type. The reg_no serves as a primary key to uniquely identify each vehicle.

# Ticket Table
# sql
# Copy code
# CREATE TABLE Ticket (
#     ticket_id VARCHAR(20) PRIMARY KEY,
#     slot_id INT,
#     reg_no VARCHAR(15),
#     issue_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (slot_id) REFERENCES ParkingSlot(slot_id),
#     FOREIGN KEY (reg_no) REFERENCES Vehicle(reg_no)
# );
# Explanation: This table records issued tickets with unique IDs that follow the format 
# <parking_lot_id>_<floor_no>_<slot_no>. slot_id and reg_no are foreign keys for 
# linking tickets to slots and vehicles, respectively.

# Example Query
# To find the number of free slots on a particular floor:

# sql
# Copy code
# SELECT COUNT(*) AS free_slots
# FROM ParkingSlot
# WHERE floor_id = <FLOOR_ID> AND is_occupied = FALSE AND slot_type = <VEHICLE_TYPE>;


from enum import Enum
from abc import ABC
from typing import List
from threading import Lock

class VehicleType(Enum):
    CAR = 1
    MOTORCYCLE = 2
    TRUCK = 3

class Vehicle(ABC):
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.type = vehicle_type

    def get_type(self) -> VehicleType:
        return self.type

class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)

class Motorcycle(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.MOTORCYCLE)

class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.TRUCK)


class ParkingSpot:
    def __init__(self, spot_number: int, vehicle_type: VehicleType):
        self.spot_number = spot_number
        self.vehicle_type = vehicle_type# Default vehicle type is CAR
        self.parked_vehicle = None
        self.spot_lock = Lock()  # Add lock for spot operations

    def is_available(self) -> bool:
        return self.parked_vehicle is None

    def park_vehicle(self, vehicle: Vehicle) -> None:
        with self.spot_lock:  # Thread-safe spot parking
            if self.is_available() and vehicle.get_type() == self.vehicle_type:
                self.parked_vehicle = vehicle
            else:
                raise ValueError("Invalid vehicle type or spot already occupied.")

    def unpark_vehicle(self) -> None:
        with self.spot_lock:  # Thread-safe spot unparking
            self.parked_vehicle = None

    def get_vehicle_type(self) -> VehicleType:
        return self.vehicle_type

    def get_parked_vehicle(self) -> Vehicle:
        return self.parked_vehicle

    def get_spot_number(self) -> int:
        return self.spot_number

class Level:
    def __init__(self, floor: int, num_spots: int):
        self.floor = floor
        self.parking_spots: List[ParkingSpot] = [ParkingSpot(i, VehicleType.CAR) if i%3==0 else ParkingSpot(i, VehicleType.MOTORCYCLE) if i%3==1 else ParkingSpot(i, VehicleType.TRUCK) for i in range(num_spots)]
        self.level_lock = Lock()  # Add lock for level operations

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        with self.level_lock:  # Thread-safe level parking
            for spot in self.parking_spots:
                if spot.is_available() and spot.get_vehicle_type() == vehicle.get_type():
                    spot.park_vehicle(vehicle)
                    return True
            return False

    def unpark_vehicle(self, vehicle: Vehicle) -> bool:
        with self.level_lock:  # Thread-safe level unparking
            for spot in self.parking_spots:
                if not spot.is_available() and spot.get_parked_vehicle() == vehicle:
                    spot.unpark_vehicle()
                    return True
            return False

    def display_availability(self) -> None:
        print(f"Level {self.floor} Availability:")
        for spot in self.parking_spots:
            print(f"Spot {spot.get_spot_number()}: {'Available' if spot.is_available() else 'Occupied'}")


class ParkingLot:
    _instance = None
    _lock = Lock()  # Class level lock

    def __init__(self):
        if ParkingLot._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ParkingLot._instance = self
            self.levels: List[Level] = []
            self.operation_lock = Lock()  # Instance level lock for parking operations

    @staticmethod
    def get_instance():
        # First check (without lock)
        if ParkingLot._instance is None:
            # Lock only if instance might need to be created
            with ParkingLot._lock:
                # Second check (with lock)
                if ParkingLot._instance is None:
                    ParkingLot()
        return ParkingLot._instance

    def add_level(self, level: Level) -> None:
        self.levels.append(level)

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        with self.operation_lock:  # Thread-safe parking operation
            for level in self.levels:
                if level.park_vehicle(vehicle):
                    return True
            return False

    def unpark_vehicle(self, vehicle: Vehicle) -> bool:
        with self.operation_lock:  # Thread-safe unparking operation
            for level in self.levels:
                if level.unpark_vehicle(vehicle):
                    return True
            return False

    def display_availability(self) -> None:
        for level in self.levels:
            level.display_availability()
    

class ParkingLotDemo:
    def run():
        parking_lot = ParkingLot.get_instance()
        parking_lot.add_level(Level(1, 5))
        parking_lot.add_level(Level(2, 5))

        car = Car("ABC123")
        truck = Truck("XYZ789")
        motorcycle = Motorcycle("M1234")

        # Park vehicles
        parking_lot.park_vehicle(car)
        parking_lot.park_vehicle(truck)
        parking_lot.park_vehicle(motorcycle)

        # Display availability
        parking_lot.display_availability()

        # Unpark vehicle
        parking_lot.unpark_vehicle(motorcycle)

        # Display updated availability
        parking_lot.display_availability()

if __name__ == "__main__":
    ParkingLotDemo.run()