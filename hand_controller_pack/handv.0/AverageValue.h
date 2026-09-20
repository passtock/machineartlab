#ifndef AVERAGE_VALUE_H
#define AVERAGE_VALUE_H

#include <Arduino.h>

template <class T>
class AverageValue {
  private:
    T* _values;
    size_t _maxValues;
    size_t _count;
    size_t _index;
    T _sum;

  public:
    AverageValue(size_t maxValues) : _maxValues(maxValues), _count(0), _index(0), _sum(0) {
      _values = new T[_maxValues];
      for (size_t i = 0; i < _maxValues; i++) {
        _values[i] = 0;
      }
    }

    ~AverageValue() {
      if (_values) {
        delete[] _values;
      }
    }

    void push(T value) {
      if (_count < _maxValues) {
        _sum += value;
        _values[_index] = value;
        _count++;
        _index = (_index + 1) % _maxValues;
      } else {
        _sum -= _values[_index];
        _values[_index] = value;
        _sum += value;
        _index = (_index + 1) % _maxValues;
      }
    }

    T average() {
      if (_count == 0) return 0;
      return _sum / (T)_count;
    }

    size_t getCount() const {
      return _count;
    }

    void reset() {
      _count = 0;
      _index = 0;
      _sum = 0;
      for (size_t i = 0; i < _maxValues; i++) {
        _values[i] = 0;
      }
    }
};

#endif // AVERAGE_VALUE_H
