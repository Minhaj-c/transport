import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/app_provider.dart';
import '../../models/route_model.dart';
import '../../widgets/loading_widget.dart';
import 'route_detail_screen.dart';

class RouteListScreen extends StatefulWidget {
  const RouteListScreen({super.key});

  @override
  State<RouteListScreen> createState() => _RouteListScreenState();
}

class _RouteListScreenState extends State<RouteListScreen> {
  final _searchController = TextEditingController();
  final _originController = TextEditingController();
  final _destinationController = TextEditingController();
  String _searchQuery = '';
  bool _showFilters = false;
  bool _filterApplied = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<AppProvider>(context, listen: false).loadRoutes();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _originController.dispose();
    _destinationController.dispose();
    super.dispose();
  }

  void _clearFilters() {
    setState(() {
      _searchController.clear();
      _originController.clear();
      _destinationController.clear();
      _searchQuery = '';
      _filterApplied = false;
    });
  }

  void _applyFilters() {
    if (_originController.text.isNotEmpty || _destinationController.text.isNotEmpty) {
      setState(() {
        _filterApplied = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Column(
      children: [
        // Search and Filter Section
        Container(
          padding: const EdgeInsets.all(16.0),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: [
              // Quick Search
              TextField(
                controller: _searchController,
                onChanged: (value) {
                  setState(() => _searchQuery = value.toLowerCase());
                },
                decoration: InputDecoration(
                  hintText: 'Search routes by name or number...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (_searchQuery.isNotEmpty)
                        IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _searchController.clear();
                            setState(() => _searchQuery = '');
                          },
                        ),
                      IconButton(
                        icon: Icon(_showFilters ? Icons.filter_alt : Icons.filter_alt_outlined),
                        onPressed: () {
                          setState(() => _showFilters = !_showFilters);
                        },
                        tooltip: 'Advanced Filters',
                      ),
                    ],
                  ),
                  filled: true,
                  fillColor: Colors.grey[100],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),

              // Advanced Filters (Origin/Destination)
              if (_showFilters) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.blue[50],
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.blue[200]!),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.filter_list, size: 20, color: Colors.blue),
                          SizedBox(width: 8),
                          Text(
                            'Where are you going?',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.blue,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      
                      // Origin Field
                      TextField(
                        controller: _originController,
                        onChanged: (value) => setState(() {}),
                        decoration: InputDecoration(
                          labelText: 'From (Starting Point)',
                          hintText: 'e.g., Central Station, Downtown',
                          prefixIcon: const Icon(Icons.trip_origin, color: Colors.green),
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      
                      // Destination Field
                      TextField(
                        controller: _destinationController,
                        onChanged: (value) => setState(() {}),
                        decoration: InputDecoration(
                          labelText: 'To (Destination)',
                          hintText: 'e.g., Airport, University',
                          prefixIcon: const Icon(Icons.location_on, color: Colors.red),
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      
                      // Action Buttons
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: _clearFilters,
                              icon: const Icon(Icons.clear_all),
                              label: const Text('Clear'),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _applyFilters,
                              icon: const Icon(Icons.search),
                              label: const Text('Find Routes'),
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],

              // Filter Status Chip
              if (_filterApplied) ...[
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.green[100],
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.check_circle, size: 16, color: Colors.green),
                      const SizedBox(width: 6),
                      Text(
                        'Showing routes: ${_originController.text.isNotEmpty ? _originController.text : "Any"} → ${_destinationController.text.isNotEmpty ? _destinationController.text : "Any"}',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Colors.green,
                        ),
                      ),
                      const SizedBox(width: 6),
                      InkWell(
                        onTap: _clearFilters,
                        child: const Icon(Icons.close, size: 16, color: Colors.green),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),

        // Route list
        Expanded(
          child: appProvider.isLoadingRoutes
              ? const LoadingWidget(message: 'Loading routes...')
              : appProvider.routes.isEmpty
                  ? const EmptyWidget(
                      message: 'No routes available',
                      icon: Icons.route,
                    )
                  : _buildRouteList(appProvider.routes),
        ),
      ],
    );
  }

  Widget _buildRouteList(List<BusRoute> routes) {
    final filteredRoutes = _filterRoutes(routes);

    if (filteredRoutes.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.search_off, size: 80, color: Colors.grey[400]),
              const SizedBox(height: 16),
              const Text(
                'No routes found',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                _filterApplied
                    ? 'No routes connect these locations.\nTry different places or clear filters.'
                    : 'Try different search terms',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey[600]),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _clearFilters,
                icon: const Icon(Icons.clear),
                label: const Text('Clear Filters'),
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => Provider.of<AppProvider>(context, listen: false).loadRoutes(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredRoutes.length,
        itemBuilder: (context, index) {
          final route = filteredRoutes[index];
          return _RouteCard(route: route);
        },
      ),
    );
  }

  List<BusRoute> _filterRoutes(List<BusRoute> routes) {
    return routes.where((route) {
      // Quick search filter
      if (_searchQuery.isNotEmpty) {
        final matchesSearch = route.number.toLowerCase().contains(_searchQuery) ||
            route.name.toLowerCase().contains(_searchQuery) ||
            route.origin.toLowerCase().contains(_searchQuery) ||
            route.destination.toLowerCase().contains(_searchQuery);
        if (!matchesSearch) return false;
      }

      // SMART FILTERING: Check if route connects origin to destination
      if (_filterApplied) {
        final originQuery = _originController.text.toLowerCase().trim();
        final destQuery = _destinationController.text.toLowerCase().trim();
        
        // Case 1: Both origin and destination specified
        if (originQuery.isNotEmpty && destQuery.isNotEmpty) {
          // Check if route has stops matching both locations
          final hasOrigin = _routePassesThroughLocation(route, originQuery);
          final hasDest = _routePassesThroughLocation(route, destQuery);
          
          // Only show route if it connects both locations
          if (!hasOrigin || !hasDest) return false;
          
          // Additional check: Make sure origin comes before destination
          final originStopIndex = _getStopIndexForLocation(route, originQuery);
          final destStopIndex = _getStopIndexForLocation(route, destQuery);
          
          if (originStopIndex >= 0 && destStopIndex >= 0) {
            if (originStopIndex >= destStopIndex) return false; // Wrong direction
          }
        }
        // Case 2: Only origin specified
        else if (originQuery.isNotEmpty) {
          if (!_routePassesThroughLocation(route, originQuery)) return false;
        }
        // Case 3: Only destination specified
        else if (destQuery.isNotEmpty) {
          if (!_routePassesThroughLocation(route, destQuery)) return false;
        }
      }

      return true;
    }).toList();
  }

  // Check if route passes through a location (checks origin, destination, and stops)
  bool _routePassesThroughLocation(BusRoute route, String location) {
    location = location.toLowerCase();
    
    // Check route origin/destination
    if (route.origin.toLowerCase().contains(location)) return true;
    if (route.destination.toLowerCase().contains(location)) return true;
    
    // Check all stops
    for (var stop in route.stops) {
      if (stop.name.toLowerCase().contains(location)) return true;
    }
    
    return false;
  }

  // Get the stop index for a location (-1 if not found)
  int _getStopIndexForLocation(BusRoute route, String location) {
    location = location.toLowerCase();
    
    // Check if it's the origin (sequence 0)
    if (route.origin.toLowerCase().contains(location)) return 0;
    
    // Check stops
    for (var stop in route.stops) {
      if (stop.name.toLowerCase().contains(location)) {
        return stop.sequence;
      }
    }
    
    // Check if it's destination (last sequence)
    if (route.destination.toLowerCase().contains(location)) {
      return route.stops.isEmpty ? 1 : route.stops.length + 1;
    }
    
    return -1;
  }
}

class _RouteCard extends StatelessWidget {
  final BusRoute route;

  const _RouteCard({required this.route});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => RouteDetailScreen(route: route),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Route number and name
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      route.number,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      route.name,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  const Icon(Icons.chevron_right),
                ],
              ),
              const SizedBox(height: 12),

              // Origin to Destination
              Row(
                children: [
                  const Icon(Icons.trip_origin, size: 16, color: Colors.green),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      route.origin,
                      style: const TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.location_on, size: 16, color: Colors.red),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      route.destination,
                      style: const TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Distance and Duration
              Row(
                children: [
                  _InfoChip(
                    icon: Icons.straighten,
                    label: route.distanceInfo,
                  ),
                  const SizedBox(width: 8),
                  _InfoChip(
                    icon: Icons.access_time,
                    label: route.durationInfo,
                  ),
                  const SizedBox(width: 8),
                  _InfoChip(
                    icon: Icons.stop_circle,
                    label: '${route.stops.length} stops',
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.grey[700]),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[700],
            ),
          ),
        ],
      ),
    );
  }
}