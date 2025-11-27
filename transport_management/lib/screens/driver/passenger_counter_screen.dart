import 'package:flutter/material.dart';

class PassengerCounterScreen extends StatefulWidget {
  const PassengerCounterScreen({super.key});

  @override
  State<PassengerCounterScreen> createState() => _PassengerCounterScreenState();
}

class _PassengerCounterScreenState extends State<PassengerCounterScreen> {
  int _currentCount = 0;
  final int _busCapacity = 40;
  final List<Map<String, dynamic>> _history = [];

  void _addPassengers(int count) {
    setState(() {
      _currentCount += count;
      if (_currentCount > _busCapacity) {
        _currentCount = _busCapacity;
      }
      _addToHistory('Added $count passenger${count > 1 ? 's' : ''}');
    });
  }

  void _removePassengers(int count) {
    setState(() {
      _currentCount -= count;
      if (_currentCount < 0) {
        _currentCount = 0;
      }
      _addToHistory('Removed $count passenger${count > 1 ? 's' : ''}');
    });
  }

  void _resetCounter() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reset Counter'),
        content: const Text('Are you sure you want to reset the counter to 0?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              setState(() {
                _currentCount = 0;
                _addToHistory('Counter reset');
              });
              Navigator.pop(context);
            },
            child: const Text(
              'Reset',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

  void _addToHistory(String action) {
    _history.insert(0, {
      'action': action,
      'count': _currentCount,
      'time': DateTime.now(),
    });
  }

  @override
  Widget build(BuildContext context) {
    final occupancyRate = (_currentCount / _busCapacity * 100).toInt();
    final availableSeats = _busCapacity - _currentCount;

    Color getOccupancyColor() {
      if (occupancyRate >= 90) return Colors.red;
      if (occupancyRate >= 70) return Colors.orange;
      return Colors.green;
    }

    return Column(
      children: [
        // Counter Display
        Expanded(
          child: Container(
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Theme.of(context).primaryColor.withOpacity(0.8),
                  Theme.of(context).primaryColor,
                ],
              ),
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Theme.of(context).primaryColor.withOpacity(0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  'Current Passengers',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 20),
                
                // Main Counter
                Text(
                  '$_currentCount',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 120,
                    fontWeight: FontWeight.bold,
                    height: 1,
                  ),
                ),
                const SizedBox(height: 10),
                
                Text(
                  'of $_busCapacity seats',
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 30),

                // Occupancy Bar
                Column(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: LinearProgressIndicator(
                        value: _currentCount / _busCapacity,
                        backgroundColor: Colors.white30,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          getOccupancyColor(),
                        ),
                        minHeight: 12,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '$occupancyRate% Full',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                // Available Seats
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '$availableSeats seats available',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),

        // Control Buttons
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Row(
                children: [
                  // Remove buttons
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _currentCount > 0 ? () => _removePassengers(1) : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 20),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Column(
                        children: [
                          Icon(Icons.remove, size: 32),
                          SizedBox(height: 4),
                          Text('Remove 1', style: TextStyle(fontSize: 12)),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  // Add buttons
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _currentCount < _busCapacity
                          ? () => _addPassengers(1)
                          : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 20),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Column(
                        children: [
                          Icon(Icons.add, size: 32),
                          SizedBox(height: 4),
                          Text('Add 1', style: TextStyle(fontSize: 12)),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _currentCount >= 5 ? () => _removePassengers(5) : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text('- 5', style: TextStyle(fontSize: 16)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _resetCounter,
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text('Reset', style: TextStyle(fontSize: 16)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _currentCount <= _busCapacity - 5
                          ? () => _addPassengers(5)
                          : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text('+ 5', style: TextStyle(fontSize: 16)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // History Button
              OutlinedButton.icon(
                onPressed: () {
                  _showHistory();
                },
                icon: const Icon(Icons.history),
                label: const Text('View History'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  minimumSize: const Size(double.infinity, 0),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _showHistory() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Passenger Count History',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Divider(),
            Expanded(
              child: _history.isEmpty
                  ? const Center(
                      child: Text('No history yet'),
                    )
                  : ListView.builder(
                      itemCount: _history.length,
                      itemBuilder: (context, index) {
                        final item = _history[index];
                        final time = item['time'] as DateTime;
                        final timeStr = '${time.hour.toString().padLeft(2, '0')}:'
                            '${time.minute.toString().padLeft(2, '0')}';
                        
                        return ListTile(
                          leading: CircleAvatar(
                            child: Text('${item['count']}'),
                          ),
                          title: Text(item['action']),
                          trailing: Text(timeStr),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}